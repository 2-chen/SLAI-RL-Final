# Remote Command Patterns — Shell Script Construction for SCO ACP

How to build remote commands and experiment shell scripts for SCO ACP execution.

## Remote Command Construction

The remote command runs inside the container. ACP 和 CCI 的 `/data/` 存储是共享的，所以脚本在容器内可以直接访问原始路径，无需复制。

Pattern:

```bash
set -euo pipefail
cd <script_directory>     # 脚本所在目录（/data/ 下原路径）
export VAR1=value1
export VAR2=value2
bash <script_name>.sh     # 脚本文件名
```

Example — 跑 `/data/homework/RL/final/launch_ood_4gpu.sh`：

```bash
set -euo pipefail
cd /data/homework/RL/final
bash launch_ood_4gpu.sh
```

Key rules:
- Always `set -euo pipefail` for strict error handling
- `cd` 到脚本所在目录（ACP 容器内可直接访问 `/data/` 下的任意路径）
- 直接 `bash <script>`，不硬编码文件名
- Export any needed environment variables before running the script
- Keep the command simple — the script handles everything else
- 仅当脚本不在 `/data/` 下时才复制到 `/data/250010008/chenresearch/`

## run_experiment.sh Requirements

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
