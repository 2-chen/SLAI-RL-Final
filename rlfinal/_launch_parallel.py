#!/usr/bin/env python3
"""Parallel experiment launcher: subprocess + thread pool, multi-GPU."""
import os, sys, subprocess, time, json, argparse
from itertools import product
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

M_VALUES = [128, 256, 512, 1024]
N_SEEDS = 20
RESULTS_DIR = "/data/homework/RL/final2/results"

print_lock = Lock()
t0_global = time.time()
EXP_TIMEOUT = int(os.environ.get("EXP_TIMEOUT", "900"))
completed_count = [0]  # mutable counter for threads
total_pending = [0]


def run_one_exp(pipeline: str, M: int, seed: int, gpu_id: int) -> tuple:
    """Run one experiment via subprocess pinned to a specific GPU. Returns (status, name, elapsed)."""
    if pipeline == "identity":
        run_name = f"identity_seed{seed}"
    elif pipeline == "compress_dqn":
        run_name = f"compress_dqn_seed{seed}"
    else:
        run_name = f"{pipeline}_M{M}_seed{seed}"

    result_path = os.path.join(RESULTS_DIR, f"{run_name}.json")
    if os.path.exists(result_path):
        with print_lock:
            completed_count[0] += 1
            print(f"[SKIP] {run_name}  [{completed_count[0]}/{total_pending[0]}]", flush=True)
        return ("skip", run_name, 0.0)

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    # Inline worker script — matches launch_all.py pattern, avoids run_one.py naming bug
    worker_code = f'''
import sys, time, traceback
sys.path.insert(0, "/data/homework/RL/final2")
from rlfinal.experiments.run_ssl_dqn import run_ssl_dqn, run_random_dqn, run_identity, run_compress_dqn

pipeline = "{pipeline}"
M = {M}
seed = {seed}
results_dir = "{RESULTS_DIR}"

if pipeline == "ssl_dqn":
    run_ssl_dqn(M, seed, "cuda:0", results_dir)
elif pipeline == "random_dqn":
    run_random_dqn(M, seed, "cuda:0", results_dir)
elif pipeline == "compress_dqn":
    run_compress_dqn(seed, "cuda:0", results_dir)
elif pipeline == "identity":
    run_identity(seed, "cuda:0", results_dir)
'''

    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "-u", "-c", worker_code],
            env=env,
            capture_output=True, text=True,
            timeout=EXP_TIMEOUT,
        )
        elapsed = time.time() - t0
        if proc.returncode == 0:
            with print_lock:
                completed_count[0] += 1
                print(f"[DONE] {run_name} ({elapsed:.0f}s)  GPU={gpu_id}  [{completed_count[0]}/{total_pending[0]}]", flush=True)
            return ("done", run_name, elapsed)
        else:
            stderr_tail = proc.stderr.strip()[-400:] if proc.stderr else "(no stderr)"
            stdout_tail = proc.stdout.strip()[-400:] if proc.stdout else "(no stdout)"
            with print_lock:
                completed_count[0] += 1
                print(f"[FAIL] {run_name} (rc={proc.returncode})  [{completed_count[0]}/{total_pending[0]}]", flush=True)
                if stdout_tail:
                    print(f"       stdout: {stdout_tail}", flush=True)
                if stderr_tail:
                    print(f"       stderr: {stderr_tail}", flush=True)
            return ("fail", run_name, elapsed)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        with print_lock:
            completed_count[0] += 1
            print(f"[TIMEOUT] {run_name} (>900s)  [{completed_count[0]}/{total_pending[0]}]", flush=True)
        return ("fail", run_name, elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        with print_lock:
            completed_count[0] += 1
            print(f"[ERROR] {run_name}: {e}  [{completed_count[0]}/{total_pending[0]}]", flush=True)
        return ("fail", run_name, elapsed)


# Will be set from main
pending_tasks = []


def main():
    global pending_tasks

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-concurrent", type=int, default=8)
    parser.add_argument("--n-gpus", type=int, default=2)
    args = parser.parse_args()

    # Build all tasks
    all_tasks = []
    for M, seed in product(M_VALUES, range(N_SEEDS)):
        for pipeline in ["ssl_dqn", "random_dqn"]:
            all_tasks.append((pipeline, M, seed))
    for seed in range(N_SEEDS):
        all_tasks.append(("compress_dqn", 16, seed))
    for seed in range(N_SEEDS):
        all_tasks.append(("identity", 64, seed))

    total = len(all_tasks)

    # Filter: skip existing unless --force
    pending_tasks = []
    for pipeline, M, seed in all_tasks:
        if pipeline == "identity":
            rpath = os.path.join(RESULTS_DIR, f"identity_seed{seed}.json")
        elif pipeline == "compress_dqn":
            rpath = os.path.join(RESULTS_DIR, f"compress_dqn_seed{seed}.json")
        else:
            rpath = os.path.join(RESULTS_DIR, f"{pipeline}_M{M}_seed{seed}.json")

        if args.force and os.path.exists(rpath):
            os.remove(rpath)

        if os.path.exists(rpath):
            continue
        pending_tasks.append((pipeline, M, seed))

    already = total - len(pending_tasks)
    total_pending[0] = len(pending_tasks)
    n_gpus = args.n_gpus
    max_workers = args.max_concurrent

    print(f"Total experiments : {total}")
    print(f"Already completed : {already}")
    print(f"Pending to run    : {len(pending_tasks)}")
    print(f"GPUs available    : {n_gpus}")
    print(f"Max concurrent    : {max_workers} ({max_workers // n_gpus} per GPU)")
    if pending_tasks:
        est = len(pending_tasks) * 150 / max_workers / 60
        print(f"Est. wall time    : ~{est:.0f} min ({est/60:.1f} h)")
    print()

    if args.dry_run:
        print("=== Dry run — task distribution (first 20 shown) ===")
        gpu = 0
        for i, (pipeline, M, seed) in enumerate(pending_tasks[:20]):
            if pipeline == "identity":
                name = f"identity_seed{seed}"
            elif pipeline == "compress_dqn":
                name = f"compress_dqn_seed{seed}"
            else:
                name = f"{pipeline}_M{M}_seed{seed}"
            print(f"  [{i+1}] {name}  -> GPU {gpu}")
            gpu = (gpu + 1) % n_gpus
        if len(pending_tasks) > 20:
            print(f"  ... and {len(pending_tasks) - 20} more")
        print(f"\nPer-GPU task count (approx): ~{len(pending_tasks) // n_gpus} each")
        return

    if not pending_tasks:
        print("All experiments already completed!")
        return

    # Submit with GPU round-robin
    gpu_counter = [0]  # mutable for closure
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for pipeline, M, seed in pending_tasks:
            gpu_id = gpu_counter[0] % n_gpus
            gpu_counter[0] += 1
            fut = executor.submit(run_one_exp, pipeline, M, seed, gpu_id)
            futures[fut] = (pipeline, M, seed)

        # Collect results
        stats = {"done": 0, "skip": 0, "fail": 0}
        total_elapsed = 0.0
        for fut in as_completed(futures):
            status, name, elapsed = fut.result()
            stats[status] += 1
            if elapsed > 0:
                total_elapsed += elapsed

    # Final summary
    wall_time = time.time() - t0_global
    print()
    print("=" * 70)
    print(f"  ALL DONE")
    print(f"  Completed : {stats['done']}")
    print(f"  Skipped   : {stats['skip']}")
    print(f"  Failed    : {stats['fail']}")
    print(f"  Wall time : {wall_time:.0f}s ({wall_time/60:.1f} min)")
    if stats['done'] > 0:
        avg = total_elapsed / stats['done']
        print(f"  Avg/exp   : {avg:.0f}s")
    print(f"  Results   : {RESULTS_DIR}/")
    print("=" * 70)

    if stats['fail'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
