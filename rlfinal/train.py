#!/usr/bin/env python3
"""Main training entry point. Run experiment matrix on available GPUs.

Usage:
    python -m rlfinal.train --M 128 256 512 1024 --seeds 5 --pipeline all
    python -m rlfinal.train --M 128 --pipeline identity --seeds 1
"""

import argparse
import os
import sys
import time
from itertools import product

import torch

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rlfinal.experiments.run_ssl_dqn import run_ssl_dqn, run_random_dqn, run_identity


def get_available_devices() -> list[str]:
    if torch.cuda.is_available():
        return [f"cuda:{i}" for i in range(torch.cuda.device_count())]
    return ["cpu"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--M", type=int, nargs="+", default=[128, 256, 512, 1024])
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--pipeline", type=str, default="all",
                        choices=["all", "ssl_dqn", "random_dqn", "identity"])
    parser.add_argument("--results-dir", type=str, default=None)
    args = parser.parse_args()

    devices = get_available_devices()
    print(f"Available devices: {devices}")

    if args.results_dir is None:
        args.results_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results"
        )

    os.makedirs(args.results_dir, exist_ok=True)

    # Build experiment list
    experiments = []
    if args.pipeline in ("all", "ssl_dqn"):
        for M, seed in product(args.M, range(args.seeds)):
            experiments.append(("ssl_dqn", M, seed))
    if args.pipeline in ("all", "random_dqn"):
        for M, seed in product(args.M, range(args.seeds)):
            experiments.append(("random_dqn", M, seed))
    if args.pipeline in ("all", "identity"):
        for seed in range(args.seeds):
            experiments.append(("identity", 64, seed))

    print(f"Total experiments: {len(experiments)}")
    print(f"Results dir: {args.results_dir}")

    # Run experiments (serial — H100 is overkill, CPU-bound on rollout)
    t_start = time.time()
    for i, (pipeline, M, seed) in enumerate(experiments):
        device = devices[i % len(devices)]
        print(f"\n[{i+1}/{len(experiments)}] {pipeline} M={M} seed={seed} on {device}")

        try:
            if pipeline == "ssl_dqn":
                run_ssl_dqn(M, seed, device, args.results_dir)
            elif pipeline == "random_dqn":
                run_random_dqn(M, seed, device, args.results_dir)
            elif pipeline == "identity":
                run_identity(seed, device, args.results_dir)
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    elapsed = time.time() - t_start
    print(f"\nAll experiments done in {elapsed:.0f}s ({elapsed/60:.1f} min)")


if __name__ == "__main__":
    main()
