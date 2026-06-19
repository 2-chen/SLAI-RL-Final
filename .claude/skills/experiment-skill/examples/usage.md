# Experiment Skill — Usage Examples

## Example 0a: Auto-Detect — Local GPU Available

**User:**
```
Submit experiment from workspace/my_project/experiment/ with name "quick-test"
```

**Skill executes:**
1. GPU Detection: `nvidia-smi -L` → 2 GPUs found (RTX 4090)
2. "Detected 2 local GPU(s). Running experiment locally."
3. Set `CUDA_VISIBLE_DEVICES=0,1`
4. Execute: `cd workspace/my_project/experiment && bash run_experiment.sh`
5. Stream stdout/stderr in real-time
6. Return: "Local run complete. PID 12345. Results in workspace/my_project/experiment/results/"

## Example 0b: Auto-Detect — No Local GPU (SCO Fallback)

**User:**
```
Submit experiment from workspace/my_project/experiment/ with name "large-run"
```

**Skill executes:**
1. GPU Detection: `nvidia-smi` not found → `torch.cuda.device_count()` → 0
2. "No local GPUs detected. Delegating to sco-skill for remote execution."
3. Load sco-skill → submit mode
4. sco-skill: copy to AFS (if local path) → submit SCO job → pt-abc123def456
5. Return: "Remote SCO job submitted via sco-skill: large-run (id=pt-abc123def456)"

## Example 0c: Force Remote Execution

**User:**
```
Submit experiment from /data/homework/RL/final/launch_ood_4gpu.sh with name "ood-test" use cloud
```

**Skill executes:**
1. User explicitly requested remote → skip GPU detection
2. Delegating to sco-skill (submit mode)...
3. sco-skill: 已在 `/data/` 下 → 直接原地执行
4. Build remote command: `cd /data/homework/RL/final && bash launch_ood_4gpu.sh`
5. Submit `sco acp jobs create ... --job-name ood-test ...`
6. Return: "Remote SCO job: ood-test (id=pt-abc123def456)"

## Example 0d: Force Local Execution

**User:**
```
Run experiment from ./experiment/ locally
```

**Skill executes:**
1. User explicitly requested local → skip GPU detection
2. Execute: `cd ./experiment && bash run_experiment.sh`
3. Return: "Local run started. PID 12346."

## Example 1: Submit and Wait

**User:**
```
Submit experiment from /data/projects/bert-finetune/train.sh with name "bert-finetune" and wait for completion
```

**Skill executes:**
1. GPU Detection: check local GPUs
2. **If local GPUs**: run locally, monitor PID, stream output
3. **If no local GPUs**: delegate to sco-skill full mode (submit → monitor → logs)
4. Report final status and results path

## Example 2: Diagnose Failed Experiment

**User:**
```
Diagnose experiment my-run-123
```

**Skill executes (local run):**
1. Check exit code and captured stderr
2. Analyze for failure patterns (OOM, missing dep, file not found, CUDA errors)
3. Output diagnostic report with suggested fixes

**Skill executes (remote SCO run):**
1. Delegate to sco-skill diagnose mode
2. sco-skill fetches SCO logs, analyzes failure patterns
3. Output diagnostic report

## Example 3: Custom GPU Configuration (Remote via sco-skill)

**User:**
```
Submit experiment from ./experiment/ with name "large-model-train" using sco with 8 GPUs and high priority
```

**Skill executes:**
1. User explicitly requested sco → delegate to sco-skill
2. sco-skill overrides: `--worker-spec n6ls.iu.i40.8.64c1024g --priority high`
3. Submit and return job ID

## Example 4: List All Runs

**User:**
```
List my experiments
```

**Skill executes:**
1. Local: `ps aux | grep "bash.*\.sh"` → 2 local runs
2. Remote: delegate to sco-skill list mode → 3 SCO jobs
3. Display combined table:

| Run ID | Name | Type | Status |
|--------|------|------|--------|
| PID 12345 | quick-test | local | Running |
| PID 12346 | eval-run | local | SUCCEEDED |
| pt-abc123 | bert-finetune | remote | RUNNING |
| pt-def456 | large-model | remote | SUCCEEDED |
| pt-ghi789 | ood-test | remote | FAILED |

## Example 5: Stop a Run

**User:**
```
Stop experiment pt-abc123def456
```

**Skill executes (remote SCO run):**
1. Detected remote SCO job → delegate to sco-skill stop mode
2. Confirm: "Stop SCO job pt-abc123def456?"
3. On confirmation: `sco acp jobs stop --workspace-name share-space pt-abc123def456`

**User:**
```
Stop experiment PID 12345
```

**Skill executes (local run):**
1. Detected local PID → confirm with user
2. `kill 12345` (SIGTERM)
3. Report: "Local run PID 12345 terminated."

## Example 6: Dry Run

**User:**
```
Show me the execution plan for submitting /data/homework/RL/final/launch_ood_4gpu.sh with name "test-dry-run"
```

**Skill executes:**
1. GPU Detection first
2. **If local GPUs**: "Dry run — would execute locally: cd /data/homework/RL/final && bash launch_ood_4gpu.sh"
3. **If no local GPUs**: "Dry run — would delegate to sco-skill: cd /data/homework/RL/final && bash launch_ood_4gpu.sh via SCO ACP"
4. "Dry run complete. No experiment submitted."
