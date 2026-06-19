#!/usr/bin/env python3
"""Parallel experiment runner: launches ALL experiments simultaneously across N GPUs."""
import os, sys, json, time, argparse
from itertools import product
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rlfinal.experiments.run_ssl_dqn import run_ssl_dqn, run_random_dqn, run_identity, run_compress_dqn


def run_one(args):
    pipeline, M, seed, results_dir, n_gpus = args
    gpu_id = seed % n_gpus
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    device = "cuda:0"

    run_name = f"{pipeline}_M{M}_seed{seed}"
    result_path = os.path.join(results_dir, f"{run_name}.json")
    if os.path.exists(result_path):
        return ("skip", run_name)

    t0 = time.time()
    try:
        if pipeline == "ssl_dqn":
            run_ssl_dqn(M, seed, device, results_dir)
        elif pipeline == "random_dqn":
            run_random_dqn(M, seed, device, results_dir)
        elif pipeline == "compress_dqn":
            run_compress_dqn(seed, device, results_dir)
        elif pipeline == "identity":
            run_identity(seed, device, results_dir)
        elapsed = time.time() - t0
        print(f"DONE {run_name} ({elapsed:.0f}s)", flush=True)
        return ("done", run_name)
    except Exception as e:
        print(f"FAIL {run_name}: {e}", flush=True)
        import traceback; traceback.print_exc()
        return ("fail", run_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--M", type=int, nargs="+", default=[128, 256, 512, 1024])
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--pipeline", type=str, default="all",
                        choices=["all", "ssl_dqn", "random_dqn", "compress_dqn", "identity"])
    parser.add_argument("--results-dir", type=str, default=None)
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    if args.results_dir is None:
        args.results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(args.results_dir, exist_ok=True)

    n_gpus = 2

    # Build experiment list
    experiments = []
    if args.pipeline in ("all", "ssl_dqn"):
        for M, seed in product(args.M, range(args.seeds)):
            experiments.append(("ssl_dqn", M, seed))
    if args.pipeline in ("all", "random_dqn"):
        for M, seed in product(args.M, range(args.seeds)):
            experiments.append(("random_dqn", M, seed))
    if args.pipeline in ("all", "compress_dqn"):
        for seed in range(args.seeds):
            experiments.append(("compress_dqn", 16, seed))
    if args.pipeline in ("all", "identity"):
        for seed in range(args.seeds):
            experiments.append(("identity", 64, seed))

    total = len(experiments)
    already = sum(1 for p, M, s in experiments
                  if os.path.exists(os.path.join(args.results_dir, f"{p}_M{M}_seed{s}.json")))
    remaining = [(p, M, s, args.results_dir, n_gpus) for p, M, s in experiments
                 if not os.path.exists(os.path.join(args.results_dir, f"{p}_M{M}_seed{s}.json"))]

    n_workers = min(args.workers or len(remaining), len(remaining))

    print(f"Total: {total}, Done: {already}, Remaining: {len(remaining)}, GPUs: {n_gpus}")
    print(f"Launching {n_workers} workers for {len(remaining)} experiments...")
    t0 = time.time()

    with Pool(processes=n_workers) as pool:
        results = pool.map(run_one, remaining)

    done = sum(1 for s, _ in results if s in ("done", "skip"))
    failed = sum(1 for s, _ in results if s == "fail")
    elapsed = time.time() - t0
    print(f"\nDone: {done}, Failed: {failed}, Time: {elapsed:.0f}s ({elapsed/60:.1f} min)")


if __name__ == "__main__":
    main()
