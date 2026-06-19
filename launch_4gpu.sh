#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="/data/homework/RL/final2:${PYTHONPATH:-}"
export CUDA_VISIBLE_DEVICES=0,1,2,3

echo "=== 4-GPU Parallel Experiment Launcher ==="
echo "Config: 4 M values x 20 seeds x 2 pipelines + 20 identity = 180 experiments"
echo "GPUs: 4x N6LS-80G (SXM5), round-robin task distribution"
echo "Results: /data/homework/RL/final2/results/"
echo "Python: $(python3 --version 2>&1)"
echo ""

# Ensure torch is available (container should have it; install as fallback)
python3 -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}, GPUs: {torch.cuda.device_count()}')" 2>/dev/null || {
    echo "Installing torch + numpy..."
    pip install torch numpy -q
}

echo ""
cd /data/homework/RL/final2
python3 -u rlfinal/launch_4gpu.py

echo ""
echo "=== Experiment complete ==="
