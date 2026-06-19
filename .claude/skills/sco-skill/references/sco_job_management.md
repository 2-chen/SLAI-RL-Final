# SCO Job Management — States, Polling, and Failure Recovery

Complete reference for managing SCO ACP jobs: state machine, polling patterns, result collection, common failures, and retry strategies.

## Job Status States

| State | Meaning |
|-------|---------|
| PENDING | Queued, waiting for resources |
| PULLING | Pulling container image |
| RUNNING | Actively executing |
| SUCCEEDED | Completed successfully (exit code 0) |
| FAILED | Completed with error (exit code ≠ 0) |
| STOPPED | Manually stopped by user |
| CANCELLED | Cancelled by system or user |

Terminal states: `SUCCEEDED`, `FAILED`, `STOPPED`, `CANCELLED`

## Polling Patterns

### Quick Check (single poll)

```bash
sco acp jobs describe --workspace-name share-space -o json <job_id> | python -c "import json,sys; print(json.load(sys.stdin).get('state','UNKNOWN'))"
```

### Wait Loop (poll until terminal)

```bash
while true; do
  STATUS=$(sco acp jobs describe --workspace-name share-space -o json <job_id> | python -c "import json,sys; print(json.load(sys.stdin).get('state','UNKNOWN'))")
  echo "$(date): $STATUS"
  case "$STATUS" in SUCCEEDED|FAILED|STOPPED|CANCELLED) break;; esac
  sleep 60
done
```

## Collect Results

After SUCCEEDED:
1. Stream logs: `sco acp jobs stream-logs --workspace-name share-space <job_id>`
2. 结果在原实验目录下（原地执行），例如 `/data/homework/RL/final/results/`
3. 仅当复制到 AFS 时结果才在 `/data/250010008/chenresearch/<job_dir>/results/`

## Common Failure Patterns

### OOM (Out of Memory)
**Symptoms**: `CUDA out of memory`, `RuntimeError: CUDA out of memory`
**Fixes**:
- Reduce batch size (e.g., 64 → 32 → 16)
- Enable gradient accumulation
- Use mixed precision training (`torch.cuda.amp`)
- Reduce model size or use gradient checkpointing

### Missing Dependencies
**Symptoms**: `ModuleNotFoundError`, `ImportError`
**Fixes**:
- Add `pip install <package>` to `run_experiment.sh`
- Pin versions for reproducibility
- Check container image has required CUDA/cuDNN versions

### File Not Found
**Symptoms**: `FileNotFoundError`, `No such file or directory`
**Fixes**:
- Use absolute paths rooted at `/data/<experiment_dir>/`
- Verify all files were copied to AFS (if local path was used)
- Check `run_experiment.sh` uses `cd` to correct directory first
- Remember: ACP/CCI 存储共享，`/data/` 下路径在容器内直接可用

### Timeout
**Symptoms**: Job killed after max runtime
**Fixes**:
- Reduce training steps/epochs
- Optimize data loading (more workers, prefetch)
- Use checkpointing to resume from saved state

### Disk Full
**Symptoms**: `No space left on device`
**Fixes**:
- Reduce checkpoint frequency or keep only best K checkpoints
- Compress logs
- Check AFS quota: `sco afs dir-quota list -i <volume_id>`

## Retry Pattern

For robust experiments, implement checkpoint-based resume:

```python
# In train.py
import os
import torch

checkpoint_path = "checkpoints/latest.pt"
start_epoch = 0

if os.path.exists(checkpoint_path):
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint["model"])
    optimizer.load_state_dict(checkpoint["optimizer"])
    start_epoch = checkpoint["epoch"] + 1
    print(f"Resumed from epoch {start_epoch}")

for epoch in range(start_epoch, max_epochs):
    train(epoch)
    torch.save({
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "epoch": epoch,
    }, checkpoint_path)
```
