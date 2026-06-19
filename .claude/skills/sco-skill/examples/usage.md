# SCO Skill — Usage Examples

These examples show direct usage of sco-skill for remote GPU execution.
For automatic GPU detection (local vs remote), use experiment-skill instead.

## Example 1: Basic SCO Submit

**User:**
```
Submit sco job from /data/homework/RL/final/launch_ood_4gpu.sh with name "ood-test"
```

**Skill executes:**
1. Verify `/data/homework/RL/final/launch_ood_4gpu.sh` exists ✓
2. 已在 `/data/` 下 → 直接原地执行，不复制
3. Build remote command: `cd /data/homework/RL/final && bash launch_ood_4gpu.sh`
4. Submit `sco acp jobs create ... --job-name ood-test ...`
5. Return: `SCO job submitted: ood-test (id=pt-abc123def456)`

**User can then:**
```
Check sco status of pt-abc123def456
```

## Example 2: Submit from Local Path (Copy to AFS)

**User:**
```
Submit sco job from workspace/my_project/experiment/ with name "diffusion-v1"
```

**Skill executes:**
1. Verify `workspace/my_project/experiment/run_experiment.sh` exists ✓
2. 路径不在 `/data/` 下 → 复制到 AFS: `/data/250010008/chenresearch/diffusion-v1_1717000000/`
3. Build remote command: `cd /data/250010008/chenresearch/diffusion-v1_1717000000 && bash run_experiment.sh`
4. Submit `sco acp jobs create ... --job-name diffusion-v1 ...`
5. Return: `SCO job submitted: diffusion-v1 (id=pt-abc123def456)`

## Example 3: Submit and Wait

**User:**
```
Submit sco job from /data/projects/bert-finetune/train.sh with name "bert-finetune" and wait for completion
```

**Skill executes:**
1. 检测到 `/data/projects/bert-finetune/train.sh` 已在共享存储 → 直接原地执行
2. Submit job: `cd /data/projects/bert-finetune && bash train.sh`
3. Enter monitor loop: poll every 60s
4. Report each status change
5. On SUCCEEDED: stream logs, report results path
6. On FAILED: stream logs, offer diagnose mode

## Example 4: Diagnose Failed SCO Job

**User:**
```
Diagnose sco job pt-abc123def456
```

**Skill executes:**
1. Fetch logs via `stream-logs`
2. Analyze for failure patterns (OOM, missing dep, file not found, etc.)
3. Output diagnostic report with specific fix suggestions

## Example 5: Custom Worker Spec

**User:**
```
Submit sco job from ./experiment/ with name "large-model-train" using 8 GPUs and high priority
```

**Skill executes:**
1. Override: `--worker-spec n6ls.iu.i40.8.64c1024g --worker-nodes 1 --priority high`
2. Submit with overridden parameters
3. Return job ID

## Example 6: List and Stop

**User:**
```
List sco jobs
```

**Skill executes:**
1. `sco acp jobs list --workspace-name share-space --page-size 20 -o json`
2. Display formatted table

**User:**
```
Stop sco job pt-abc123def456
```

**Skill executes:**
1. Confirm with user: "Stop SCO job pt-abc123def456? This action cannot be undone."
2. On confirmation: `sco acp jobs stop --workspace-name share-space pt-abc123def456`
3. Report: "SCO job pt-abc123def456 stopped."

## Example 7: Dry Run

**User:**
```
Show me the SCO command for submitting /data/homework/RL/final/launch_ood_4gpu.sh with name "test-dry-run"
```

**Skill executes:**
1. 检测到已在 `/data/` 下 → 原地执行，不复制
2. Build full `sco acp jobs create ...` command with `--command "set -euo pipefail\ncd /data/homework/RL/final\nbash launch_ood_4gpu.sh"`
3. Print it without executing
4. "Dry run — no job submitted. Run without --dry-run to submit."
