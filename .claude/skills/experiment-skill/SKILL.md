---
name: experiment-skill
description: "GPU experiment execution with auto-detection of available GPUs. If local GPUs are available (detected via nvidia-smi or torch.cuda), runs experiments directly on the local machine for fast iteration. If no local GPUs, delegates to sco-skill for remote execution on SenseCore SCO ACP cluster. 7 modes: submit, monitor, logs, list, stop, diagnose, full. Triggers on: submit experiment, run experiment, GPU training, local GPU, auto GPU, 提交实验, 运行实验, 本地训练."
metadata:
  version: "1.1"
  last_updated: "2026-05-31"
  depends_on: "sco-skill (for remote GPU fallback)"
---

# Experiment Skill — GPU Experiment Runner (Local-First)

Runs machine learning experiments with automatic GPU detection. **Local-first**: checks `nvidia-smi` for available GPUs and runs experiments directly on the local machine. Falls back to `sco-skill` for remote GPU execution on the SenseCore cluster only when no local GPUs are available.

## Quick Start

**Minimal command (auto-detect GPU):**
```
Submit experiment from /path/to/experiment/ with name "my_experiment"
```

**Force remote execution:**
```
Submit experiment from /path/to/experiment/ with name "my_experiment" use cloud
```

**Force local execution:**
```
Run experiment from /path/to/experiment/ locally
```

**Execution flow:**
1. Validate experiment directory (must contain at least one `.sh` script)
2. **GPU Detection**: Check local GPU availability via `nvidia-smi` / `torch.cuda`
3. **Local GPUs available** → run experiment locally with `CUDA_VISIBLE_DEVICES` set
4. **No local GPUs** → delegate to `sco-skill` for remote SCO ACP execution
5. Monitor execution (local process or remote SCO job) until terminal state
6. Stream logs and collect results

---

## Trigger Conditions

### Trigger Keywords

**English**: submit experiment, run experiment, GPU training, GPU experiment, launch experiment, start training, submit training job, check experiment status, experiment logs, stop experiment, list experiments, diagnose experiment, local GPU, auto GPU, local training, run locally, detect GPU

**繁體中文**: 提交實驗, 運行實驗, GPU訓練, 實驗狀態, 實驗日誌, 停止實驗, 列出實驗, 本地GPU, 本地訓練, 自動檢測

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Literature search / finding papers | `search-skill` |
| Writing a paper | `write-skill` |
| Peer review of a paper | `review-skill` |
| Full research pipeline | `pipeline-skill` |
| Direct SCO job submission / management | `sco-skill` |
| SCO resource management (list/describe/CCI/AFS) | `sco-skill` |

---

## Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| `submit` | "submit experiment", "run experiment" | Detect GPUs → run locally OR delegate to sco-skill for remote |
| `monitor` | "check status", "wait for experiment" | Poll local process or remote SCO job until terminal state |
| `logs` | "get logs", "stream logs" | Stream output from local process or fetch remote SCO logs |
| `list` | "list experiments", "show runs" | List running local processes and/or recent SCO jobs |
| `stop` | "stop experiment", "cancel run" | Kill local process or stop remote SCO job |
| `diagnose` | "diagnose experiment", "debug run" | Analyze local logs or remote SCO logs, suggest fixes |
| `full` | "submit and wait", "run and monitor" | submit → monitor → logs → report |

Default mode: `full` (submit + monitor + logs).

---

## GPU Detection Logic

### Auto-Detection (default on submit)

When the user submits an experiment, the skill first determines where to run:

```bash
# Step 1: Try nvidia-smi
GPU_COUNT=$(nvidia-smi -L 2>/dev/null | wc -l)

# Step 2: Fallback to torch.cuda
if [ "$GPU_COUNT" -eq 0 ]; then
    GPU_COUNT=$(python3 -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo 0)
fi
```

**Decision:**
- `GPU_COUNT > 0` → "Detected N local GPU(s). Running experiment locally."
- `GPU_COUNT == 0` → "No local GPUs detected. Delegating to sco-skill for remote execution on SenseCore."

### Explicit Override

Users can force execution mode regardless of detection:

| User says | Behavior |
|-----------|----------|
| "run locally", "force local", "local GPU" | Skip detection, run locally |
| "use cloud", "use sco", "remote GPU", "run remotely" | Skip detection, delegate to sco-skill |

---

## Workflow Detail

### Mode: submit

1. Verify experiment directory exists and contains at least one `.sh` script
2. Detect the entrypoint script:
   - If a single `.sh` file exists, use it directly
   - If multiple `.sh` files exist, map user intent to script name (e.g., "run training" → `train.sh`, "run eval" → `eval.sh`)
3. Generate job name (user-provided or auto-generated from directory name + timestamp)
4. **GPU Detection** (skip if user explicitly overrides):
   - Run `nvidia-smi -L` → count GPUs
   - Fallback: `python3 -c "import torch; print(torch.cuda.device_count())"`
5. **Branch: Local Execution** (GPUs detected OR user forced local):
   - Set `CUDA_VISIBLE_DEVICES=0,1,...,N-1`
   - `cd <script_directory> && bash <script_name>.sh`
   - Capture PID, stream stdout/stderr
   - Return: "Local run started. PID: <pid>. Results in <script_directory>/results/"
6. **Branch: Remote Execution** (no GPUs OR user forced remote):
   - Load `sco-skill` SKILL.md and follow its **submit** mode workflow
   - sco-skill handles: AFS path detection, remote command construction, `sco acp jobs create`
   - Return: "Remote SCO job submitted: <job_name> (id=<sco_job_id>)"

### Mode: monitor

**Local run:**
1. Check if process is alive: `ps -p <pid>` or `kill -0 <pid>`
2. If alive → "Running (PID <pid>, CPU: X%, MEM: Y%)"
3. If exited → check exit code: 0 = SUCCEEDED, non-zero = FAILED
4. Poll interval: 10s (local runs are faster to complete)

**Remote run (delegate to sco-skill):**
1. Load `sco-skill` SKILL.md and follow its **monitor** mode
2. Poll `sco acp jobs describe` every 60s
3. Report SCO job status: PENDING → RUNNING → SUCCEEDED / FAILED / STOPPED
4. Timeout after 24h

### Mode: logs

**Local run:**
1. Read captured stdout/stderr from the local process
2. Or tail the log file: `tail -f <experiment_dir>/results/run.log`

**Remote run (delegate to sco-skill):**
1. Load `sco-skill` SKILL.md and follow its **logs** mode
2. Run `sco acp jobs stream-logs --workspace-name share-space <job_id>`
3. Save to file if output path specified

### Mode: list

1. List local running experiment processes: `ps aux | grep "bash.*\.sh"`
2. List recent SCO jobs (delegate to sco-skill **list** mode)
3. Display combined table: Run ID, Name, Type (local/remote), Status

### Mode: stop

**Local run:**
1. Confirm with user
2. `kill <pid>` (SIGTERM first, then SIGKILL after 10s)

**Remote run (delegate to sco-skill):**
1. Confirm with user
2. Load `sco-skill` SKILL.md and follow its **stop** mode

### Mode: diagnose

**Local run:**
1. Check exit code and captured stderr
2. Analyze for common failure patterns (OOM, missing dep, file not found, CUDA errors)
3. Output diagnostic report with suggested fixes

**Remote run (delegate to sco-skill):**
1. Load `sco-skill` SKILL.md and follow its **diagnose** mode
2. Fetch SCO logs, analyze failure patterns, suggest fixes

### Mode: full

Execute sequentially: submit → monitor → logs → report final status and results location.

---

## Remote Execution (via sco-skill)

When local GPUs are unavailable, experiment-skill delegates to [sco-skill](../../sco-skill/SKILL.md), which provides:

- SCO ACP job submission with 2chen defaults (share-space, share-cluster, 4× N6LS-80G)
- AFS shared storage handling (`/data/` paths run in-place, no copy needed)
- Job monitoring, log streaming, and diagnostics
- Full SCO configuration reference and worker spec options

See [sco-skill SKILL.md](../../sco-skill/SKILL.md) for:
- Default SCO configuration (workspace, cluster, image, worker specs)
- Environment variable overrides (`SCO_WORKSPACE`, `SCO_WORKER_SPEC`, etc.)
- Full `sco acp jobs create` command reference
- Job management commands (describe, stream-logs, list, stop)

To use sco-skill directly (bypass GPU detection):
```
Submit sco job from /data/homework/RL/final/launch_ood_4gpu.sh with name "ood-test"
```

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
- Work both locally (with `CUDA_VISIBLE_DEVICES` set) and remotely (inside SCO container)

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
2. **GPU detection first**: always check local GPUs before delegating to remote — local execution is faster and free
3. **Dry-run first**: offer `--dry-run` to preview execution plan (local command or SCO command)
4. **Confirm destructive ops**: stop requires explicit user confirmation for both local and remote runs
5. **Don't assume success**: always check execution status, don't claim success without verification
6. **Preserve experiment code**: never modify experiment files without user approval
7. **Local process cleanup**: ensure local subprocesses are properly terminated on stop or error

---

## Reference Loading

- Read [experiment_pattern.md](references/experiment_pattern.md) for experiment design patterns and best practices
- For remote GPU execution details, read [sco-skill SKILL.md](../../sco-skill/SKILL.md) and its references:
  - [sco_config.md](../../sco-skill/references/sco_config.md) — full SCO configuration
  - [sco_job_management.md](../../sco-skill/references/sco_job_management.md) — job states, polling, failure recovery
  - [remote_command_patterns.md](../../sco-skill/references/remote_command_patterns.md) — remote command construction

## Template Loading

- Use [run_experiment.sh.j2](templates/run_experiment.sh.j2) when generating a new experiment shell script
