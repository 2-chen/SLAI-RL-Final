"""
SCO CLI wrapper for ChenResearch experiment execution.
Imports defaults from config.py; everything overridable via env vars.
"""

import subprocess
import time
import json
import logging
import shutil
from pathlib import Path
from dataclasses import dataclass

import sys as _sys
from pathlib import Path as _Path
_srcdir = _Path(__file__).resolve().parent.parent
if str(_srcdir) not in _sys.path:
    _sys.path.insert(0, str(_srcdir))
from shared.config import (
    SCO_WORKSPACE, SCO_AEC2, SCO_IMAGE,
    SCO_WORKER_SPEC, SCO_STORAGE_MOUNT, SCO_WORKER_NODES,
    SCO_QUOTA_TYPE, SCO_PRIORITY,
)

logger = logging.getLogger(__name__)

JOB_STATE_TERMINAL = {"SUCCEEDED", "FAILED", "STOPPED", "CANCELLED"}


@dataclass
class SCOConfig:
    workspace: str = SCO_WORKSPACE
    aec2: str = SCO_AEC2
    image: str = SCO_IMAGE
    worker_spec: str = SCO_WORKER_SPEC
    storage_mount: str = SCO_STORAGE_MOUNT
    worker_nodes: int = SCO_WORKER_NODES
    quota_type: str = SCO_QUOTA_TYPE
    priority: str = SCO_PRIORITY
    training_framework: str = "pytorch"


@dataclass
class SCOJob:
    job_id: str
    job_name: str
    status: str = "PENDING"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def submit_job(
    script_path: str | Path,
    job_name: str,
    extra_env: dict[str, str] | None = None,
    config: SCOConfig | None = None,
    dry_run: bool = False,
) -> SCOJob:
    """
    提交 ACP 任务。

    ACP 和 CCI 的存储空间是共享的（/data/ 挂载的是同一个 AFS），
    所以如果脚本已经在 /data/ 下，直接原地 cd && bash 即可，不需要 cp。

    仅当脚本在本地非 /data/ 路径时才复制到 AFS。
    """
    if shutil.which("sco") is None:
        raise RuntimeError("sco CLI not found on PATH")

    cfg = config or SCOConfig()
    script_path = Path(script_path).resolve()
    script_name = script_path.name

    # 判断是否已在共享存储上
    if str(script_path).startswith("/data/"):
        # ACP / CCI 存储共享，直接原地执行，无需复制
        work_dir = str(script_path.parent)
        logger.info("Script is on shared storage, running in-place: %s", work_dir)
    else:
        # 本地路径 → 复制到 AFS
        import time
        work_dir = f"{AFS_BASE}/{job_name}_{int(time.time())}"
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        experiment_dir = script_path.parent
        shutil.copytree(experiment_dir, work_dir, dirs_exist_ok=True)
        logger.info("Experiment directory copied to AFS: %s", work_dir)

    command = _build_remote_command(work_dir, script_name, extra_env or {})

    cmd = [
        "sco", "acp", "jobs", "create",
        "--workspace-name", cfg.workspace,
        "--aec2-name", cfg.aec2,
        "--job-name", job_name,
        "--container-image-url", cfg.image,
        "--training-framework", cfg.training_framework,
        "--worker-nodes", str(cfg.worker_nodes),
        "--worker-spec", cfg.worker_spec,
        "--priority", cfg.priority,
        "--quota-type", cfg.quota_type,
        "--storage-mount", cfg.storage_mount,
        "--command", command,
    ]

    if dry_run:
        logger.info("[DRY RUN] %s", " ".join(cmd))
        return SCOJob(job_id="dry-run-0", job_name=job_name)

    logger.info("Submitting SCO job: %s", job_name)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"sco submit failed: {result.stderr}")

    job_id = _parse_job_id(result.stdout)
    logger.info("Job submitted: %s (id=%s)", job_name, job_id)
    return SCOJob(job_id=job_id, job_name=job_name)


def get_job_status(job_id: str, config: SCOConfig | None = None) -> str:
    cfg = config or SCOConfig()
    result = subprocess.run(
        ["sco", "acp", "jobs", "describe", "--workspace-name", cfg.workspace,
         "-o", "json", job_id],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"sco describe failed: {result.stderr}")
    data = json.loads(result.stdout)
    return data.get("status", data.get("state", "UNKNOWN"))


def wait_for_job(
    job_id: str,
    poll_interval: int = 60,
    max_wait: int = 86400,
    config: SCOConfig | None = None,
) -> SCOJob:
    """Poll until job reaches a terminal state."""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        status = get_job_status(job_id, config)
        logger.info("Job %s status: %s", job_id, status)
        if status in JOB_STATE_TERMINAL:
            return SCOJob(job_id=job_id, job_name="", status=status)
        time.sleep(poll_interval)
    raise TimeoutError(f"Job {job_id} did not finish within {max_wait}s")


def stream_logs(
    job_id: str,
    output_path: str | Path | None = None,
    config: SCOConfig | None = None,
) -> str:
    cfg = config or SCOConfig()
    result = subprocess.run(
        ["sco", "acp", "jobs", "stream-logs", "--workspace-name", cfg.workspace, job_id],
        capture_output=True, text=True, timeout=120,
    )
    logs = result.stdout
    if output_path:
        Path(output_path).write_text(logs)
    return logs


def list_jobs(limit: int = 20, config: SCOConfig | None = None) -> list[dict]:
    cfg = config or SCOConfig()
    result = subprocess.run(
        ["sco", "acp", "jobs", "list", "--workspace-name", cfg.workspace,
         "--page-size", str(limit), "-o", "json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"sco list failed: {result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip() else []


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

AFS_BASE = "/data/250010008/chenresearch"


def _build_remote_command(work_dir: str, script_name: str, extra_env: dict[str, str]) -> str:
    """
    构建远程执行命令：cd 到脚本所在目录，然后 bash 执行。
    ACP/CCI 存储共享，/data/ 下的路径在容器内可直接访问。
    """
    lines = ["set -euo pipefail"]
    lines.append(f"cd {work_dir}")
    for k, v in (extra_env or {}).items():
        lines.append(f"export {k}={v}")
    lines.append(f"bash {script_name}")
    return "\n".join(lines)


def _parse_job_id(stdout: str) -> str:
    try:
        data = json.loads(stdout)
        if isinstance(data, dict):
            return data.get("job_id") or data.get("id") or data.get("name", "")
    except json.JSONDecodeError:
        pass
    # "job pt-xxx submitted successfully, ..." → second word
    for line in stdout.strip().splitlines():
        line = line.strip()
        if line.startswith("job ") and "submitted" in line:
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]
    for line in stdout.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("+") and not line.startswith("|"):
            parts = line.split()
            if parts:
                return parts[0]
    return stdout.strip().split()[-1] if stdout.strip() else "unknown"
