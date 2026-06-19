# Experiment Workflow Patterns

Best practices and common patterns for designing experiments that run on SCO ACP.

## Experiment Lifecycle

```
Design → Code → Package → Submit → Monitor → Collect → Analyze → Iterate
```

Each stage has specific deliverables and validation checks.

## Stage 1: Design

Before writing code, define:
- Research question and hypothesis
- Independent variables (what you manipulate)
- Dependent variables (what you measure)
- Controlled variables (what stays fixed)
- Number of runs/seeds for statistical significance

## Stage 2: Code Structure

Recommended experiment directory layout:

```
experiment/
├── run_experiment.sh      # Entry point (REQUIRED)
├── train.py               # Main training script
├── evaluate.py            # Evaluation script
├── model.py               # Model definition
├── data.py                # Data loading/preprocessing
├── utils.py               # Utilities
├── config.yaml            # Configuration (hyperparams, paths)
├── requirements.txt       # Python dependencies
└── README.md              # Experiment notes (optional)
```

## Stage 3: run_experiment.sh Requirements

The shell script is the single entry point. It must:

1. **Set strict mode**: `set -euo pipefail`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Set environment variables**: wandb keys, data paths, etc.
4. **Run experiments**: sequential or parallel, with proper logging
5. **Save results**: structured output directory
6. **Exit correctly**: 0 on success, non-zero on failure

Pattern:
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Experiment: <name> ==="
echo "Start: $(date)"

# Environment
export WANDB_API_KEY="${WANDB_API_KEY:-}"
export PYTHONUNBUFFERED=1

# Dependencies
pip install -r requirements.txt --quiet

# Run
python train.py \
  --config config.yaml \
  --output ./results/ \
  2>&1 | tee ./results/train.log

echo "Done: $(date)"
```

## Stage 4: Submit

Use the experiment-skill to submit:

```
Submit experiment from /data/projects/<topic>/run.sh with name "cr-<topic>-v1"
```

The skill will:
1. **GPU Detection**: Check local GPUs via `nvidia-smi` / `torch.cuda`
2. **Local GPUs available** → run experiment locally with `CUDA_VISIBLE_DEVICES` set
3. **No local GPUs** → delegate to `sco-skill` for remote execution on SenseCore SCO ACP
4. Return execution run ID (local PID or remote SCO job ID)

**GPU Auto-Detection**: experiment-skill automatically chooses local vs remote. Use "run locally" or "use cloud" to force a specific mode. See [experiment-skill SKILL.md](../SKILL.md) for full GPU detection logic.

For direct remote execution (bypass GPU detection), use sco-skill:
```
Submit sco job from /data/projects/<topic>/run.sh with name "cr-<topic>-v1"
```

## Stage 5: Monitor

Monitor experiment execution via experiment-skill (monitor mode):

- **Local runs**: experiment-skill polls the local process (`ps -p <pid>`) every 10s
- **Remote SCO jobs**: experiment-skill delegates to sco-skill, which polls `sco acp jobs describe` every 60s

For remote job monitoring patterns, see [sco-skill references](../../sco-skill/references/sco_job_management.md).

## Stage 6: Collect Results

After SUCCEEDED:
1. Stream logs via experiment-skill (logs mode)
2. **Local runs**: results in `<experiment_dir>/results/`
3. **Remote runs**: results in original directory (ACP/CCI 存储共享) or AFS path if copied

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
- Verify all files were copied to AFS
- Check `run_experiment.sh` uses `cd` to correct directory first

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

## Multi-Run Experiments

For hyperparameter sweeps or multiple seeds:

```bash
#!/usr/bin/env bash
set -euo pipefail

SEEDS=(42 123 456 789 1024)
LEARNING_RATES=(1e-4 3e-4 1e-3)

for lr in "${LEARNING_RATES[@]}"; do
  for seed in "${SEEDS[@]}"; do
    echo "=== lr=$lr seed=$seed ==="
    python train.py --lr "$lr" --seed "$seed" --output "./results/lr${lr}_seed${seed}/"
  done
done

# Aggregate results
python aggregate_results.py --input ./results/ --output ./results/summary.json
```

## Environment Variables Reference

Common environment variables to set in `run_experiment.sh`:

| Variable | Purpose |
|----------|---------|
| `PYTHONUNBUFFERED=1` | Real-time log output |
| `CUDA_VISIBLE_DEVICES` | GPU selection |
| `WANDB_API_KEY` | Weights & Biases logging |
| `WANDB_MODE` | Set to `offline` if no internet |
| `OMP_NUM_THREADS` | Limit OpenMP threads |
| `TORCH_HOME` | PyTorch cache directory |
| `HF_HOME` | HuggingFace cache directory |
