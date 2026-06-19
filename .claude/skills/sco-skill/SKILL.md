---
name: sco-skill
description: "Remote GPU experiment execution on SenseCore SCO ACP cluster. Handles the full remote job lifecycle: prepare experiment directory → submit to SCO ACP → monitor job status → stream logs → collect results. Uses 2chen defaults (share-space / share-cluster / 4× N6LS-80G). 7 modes: submit, monitor, logs, list, stop, diagnose, full. Standalone skill for direct SCO/ACP remote GPU execution. Called by experiment-skill as the remote fallback when no local GPUs are available. Triggers on: sco job, remote gpu, acp job, submit sco, sco experiment, sensecore, sco命令, 远程GPU, cloud job, submit acp, sco submit."
metadata:
  version: "1.0"
  last_updated: "2026-05-31"
  depends_on: "sco CLI (installed and authenticated on SenseCore)"
---

# SCO Skill — SenseCore ACP Remote GPU Runner

Submits and manages machine learning experiments on the SenseCore GPU cluster via `sco acp` CLI. This is the **remote execution layer** — it handles SCO job submission, monitoring, log streaming, and diagnostics. It does NOT handle GPU detection; for auto-detection of local vs remote GPUs, use `experiment-skill`.

## Quick Start

**Minimal command:**
```
Submit sco job from /path/to/experiment/ with name "my_experiment"
```

**With monitoring:**
```
Submit sco job from /path/to/experiment/ with name "my_experiment" and wait for completion
```

**Execution flow:**
1. Validate experiment directory (must contain at least one `.sh` script)
2. **ACP/CCI 存储共享**: `/data/` 下的脚本直接原地执行（`cd <dir> && bash <script>.sh`），无需 cp
3. 仅当脚本在本地非 `/data/` 路径时才复制到 AFS (`/data/250010008/chenresearch/`)
4. Submit SCO ACP job with 2chen defaults
5. Optionally monitor until terminal state
6. Stream logs and collect results

---

## Trigger Conditions

### Trigger Keywords

**English**: sco job, remote gpu, acp job, sco experiment, sensecore, cloud experiment, cloud training, submit sco, submit acp, sco submit, remote training, sco acp, check sco job, sco logs, sco list, sco stop, stop sco job, afs, sco config, remote execution

**繁體中文**: SCO任务, 远程GPU, 云实验, 云训练, SCO提交, SCO日志, SCO状态, 遠程GPU

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Local GPU experiment execution | `experiment-skill` |
| Full research pipeline | `pipeline-skill` |
| Literature search / finding papers | `search-skill` |
| Writing a paper | `write-skill` |
| Peer review of a paper | `review-skill` |

---

## Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| `submit` | "submit sco job", "submit acp job", "remote experiment" | Validate, copy to AFS (if needed), submit SCO job, return job ID |
| `monitor` | "check sco status", "wait for sco job" | Poll job status until terminal state |
| `logs` | "get sco logs", "stream sco logs" | Fetch and display job logs |
| `list` | "list sco jobs", "show sco jobs" | List recent SCO ACP jobs |
| `stop` | "stop sco job", "cancel sco job" | Stop a running SCO job |
| `diagnose` | "diagnose sco job", "debug sco job" | Fetch logs, analyze errors, suggest fixes |
| `full` | "submit sco and wait", "remote run and monitor" | submit → monitor → logs → report |

Default mode: `full` (submit + monitor + logs).

---

## Default Configuration (2chen)

All defaults from ChenResearch config. Overridable via environment variables or explicit user request.

| Parameter | Default Value |
|-----------|--------------|
| `--workspace-name` | `share-space` |
| `--aec2-name` | `share-cluster` |
| `--container-image-url` | `registry.cn-sh-01.sensecore.cn/ccr-zhicheng-02/chen-mirror2:2chen-mini-20260410132739` |
| `--worker-spec` | `n6ls.iu.i40.4.32c512g` (4× N6LS-80G-SXM5, 32 vCPU, 512GB) |
| `--storage-mount` | `01995892-d478-76d8-aec7-13fd8284477e:/data:/250010008` |
| `--quota-type` | `reserved` |
| `--priority` | `normal` |
| `--training-framework` | `pytorch` |
| `--worker-nodes` | `1` |
| AFS base path | `/data/250010008/chenresearch` |

### Environment Variable Overrides

```bash
export SCO_WORKSPACE=share-space
export SCO_AEC2=share-cluster
export SCO_IMAGE=registry.cn-sh-01.sensecore.cn/ccr-zhicheng-02/chen-mirror2:2chen-mini-20260410132739
export SCO_WORKER_SPEC=n6ls.iu.i40.4.32c512g
export SCO_STORAGE_MOUNT=01995892-d478-76d8-aec7-13fd8284477e:/data:/250010008
export SCO_WORKER_NODES=1
export SCO_QUOTA_TYPE=reserved
export SCO_PRIORITY=normal
```

---

## Workflow Detail

### Mode: submit

1. Verify `sco` CLI is available on PATH (`which sco`)
2. Verify experiment directory exists and contains at least one `.sh` script
3. Detect the entrypoint script:
   - If a single `.sh` file exists, use it directly
   - If multiple `.sh` files exist, the user's experiment intent determines which one — e.g., "run the training experiment" → `train.sh`, "run the eval" → `eval.sh`. The skill maps the user's stated goal to the matching script, not by asking the user to pick a file
4. Generate job name (user-provided or auto-generated from directory name + timestamp)
5. **路径判断（ACP/CCI 存储共享）**:
   - **已在 `/data/` 下** → 直接原地执行，无需复制。例如 `/data/homework/RL/final/launch_ood_4gpu.sh` → `cd /data/homework/RL/final && bash launch_ood_4gpu.sh`
   - **本地路径（不在 `/data/` 下）** → 复制整个实验目录到 AFS: `/data/250010008/chenresearch/<job_name>_<timestamp>/`
6. Build remote command:
   ```bash
   set -euo pipefail
   cd <script_directory>    # 脚本所在的原始目录（/data/ 下）
   bash <script_name>.sh    # 脚本文件名
   ```
7. Run:
   ```bash
   sco acp jobs create \
     --workspace-name share-space \
     --aec2-name share-cluster \
     --job-name <job_name> \
     --container-image-url <image> \
     --training-framework pytorch \
     --worker-nodes 1 \
     --worker-spec n6ls.iu.i40.4.32c512g \
     --priority normal \
     --quota-type reserved \
     --storage-mount 01995892-d478-76d8-aec7-13fd8284477e:/data:/250010008 \
     --command "<remote_command>"
   ```
8. Parse job ID from output, return to user

### Mode: monitor

1. Poll `sco acp jobs describe --workspace-name share-space -o json <job_id>` every 60s
2. Report status each poll: PENDING → RUNNING → SUCCEEDED / FAILED / STOPPED
3. Timeout after 24h (configurable)
4. Return final status

Job state machine:
```
PENDING → PULLING → RUNNING → {SUCCEEDED, FAILED, STOPPED, CANCELLED}
```

### Mode: logs

1. Run `sco acp jobs stream-logs --workspace-name share-space <job_id>`
2. Save to file if output path specified
3. Display last N lines if requested

### Mode: list

1. Run `sco acp jobs list --workspace-name share-space --page-size 20 -o json`
2. Format and display job ID, name, status, creation time

### Mode: stop

1. Confirm with user (destructive operation)
2. Run `sco acp jobs stop --workspace-name share-space <job_id>`

### Mode: diagnose

1. Fetch logs via `stream-logs`
2. Analyze for common failure patterns:
   - Missing dependencies → suggest `pip install` additions
   - OOM → suggest reducing batch size or model size
   - File not found → suggest path fixes
   - Syntax errors → identify file and line
   - CUDA errors → check driver/version compatibility
3. Output diagnostic report with suggested fixes

### Mode: full

Execute sequentially: submit → monitor → logs → report final status and results location.

---

## Experiment Directory Requirements

A valid experiment directory must contain at least one `.sh` script:

```
experiment/
├── run_experiment.sh    # Recommended name, but any .sh file works
├── *.py                  # Python training/evaluation scripts
├── requirements.txt      # Optional: pip dependencies
└── config.yaml           # Optional: experiment configuration
```

The entrypoint `.sh` script must:
- Be self-contained (install deps, run all experiments, save results)
- Exit with code 0 on success, non-zero on failure
- Save results to a structured output directory
- Work with `bash <script>.sh` from its own directory (the skill will cd to its path)

**ACP/CCI 存储共享**：`/data/` 下的实验目录在 ACP 容器内可直接访问，无需复制。仅当实验目录在本地非 `/data/` 路径时才复制到 AFS (`/data/250010008/chenresearch/`)。

Minimal example:
```bash
#!/usr/bin/env bash
set -euo pipefail
pip install -r requirements.txt
python train.py --output ./results/
echo "Experiment complete. Results in ./results/"
```

---

## Safety Rules

1. **Validate before submit**: experiment dir must exist and contain at least one `.sh` script
2. **原地执行优先**: ACP/CCI 存储共享，`/data/` 下的脚本直接 `cd <dir> && bash <script>`，不复制
3. **Dry-run first**: offer `--dry-run` to preview the SCO command without submitting
4. **Confirm destructive ops**: stop/delete require explicit user confirmation
5. **Don't assume success**: always check job status after submission, don't claim success without verification
6. **Preserve experiment code**: never modify experiment files without user approval
7. **Quota awareness**: default to `reserved` quota; only use `spot` if user explicitly requests it

---

## Reference Loading

- Read [sco_config.md](references/sco_config.md) for full SCO configuration details and available worker specs
- Read [sco_job_management.md](references/sco_job_management.md) for job state management, polling patterns, and failure recovery
- Read [remote_command_patterns.md](references/remote_command_patterns.md) for remote command construction and experiment shell script patterns

## Template Loading

- Use [run_experiment.sh.j2](templates/run_experiment.sh.j2) when generating a new experiment shell script for remote execution
