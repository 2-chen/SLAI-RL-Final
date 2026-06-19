#!/usr/bin/env python3
"""Launch 180 experiments across 4 GPUs in parallel, each GPU sequential.

Total: 4 M × 20 seeds × 2 pipelines (ssl_dqn, random_dqn) + 20 identity = 180
Per GPU: ~45 experiments, est. ~2.5h wall time at ~200s/experiment.
"""
import os, sys, subprocess, time, json, select
from itertools import product

M_VALUES = [128, 256, 512, 1024]
N_SEEDS = 20
RESULTS_DIR = "/data/homework/RL/final2/results"
N_GPUS = 4

WORKER_SCRIPT = r'''#!/usr/bin/env python3 -u
import os, sys, json, time, traceback
gpu_id = sys.argv[1]
os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
sys.path.insert(0, "/data/homework/RL/final2")
from rlfinal.experiments.run_ssl_dqn import run_ssl_dqn, run_random_dqn, run_identity, run_compress_dqn

tasks_file = sys.argv[2]
results_dir = sys.argv[3]
tasks = json.loads(open(tasks_file).read())

print(f"[GPU {gpu_id}] {len(tasks)} experiments queued", flush=True)
t_start = time.time()
ok = skip = fail = 0

for i, task in enumerate(tasks):
    name, pipeline, M, seed = task
    if pipeline == "compress_dqn":
        rname = f"compress_dqn_seed{seed}"
    elif pipeline == "identity":
        rname = f"identity_seed{seed}"
    else:
        rname = f"{pipeline}_M{M}_seed{seed}"
    rpath = os.path.join(results_dir, f"{rname}.json")
    if os.path.exists(rpath):
        skip += 1
        continue

    t0 = time.time()
    try:
        if pipeline == "ssl_dqn":
            run_ssl_dqn(M, seed, "cuda:0", results_dir)
        elif pipeline == "random_dqn":
            run_random_dqn(M, seed, "cuda:0", results_dir)
        elif pipeline == "compress_dqn":
            run_compress_dqn(seed, "cuda:0", results_dir)
        elif pipeline == "identity":
            run_identity(seed, "cuda:0", results_dir)
        ok += 1
        elapsed = time.time() - t0
        remaining = len(tasks) - i - 1
        eta = elapsed * remaining
        done_count = ok + skip + fail
        print(f"[GPU {gpu_id}] [{done_count}/{len(tasks)}] {name} DONE ({elapsed:.0f}s) ETA:{eta/60:.0f}min", flush=True)
    except Exception as e:
        fail += 1
        traceback.print_exc()
        print(f"[GPU {gpu_id}] [{ok+skip+fail}/{len(tasks)}] {name} FAIL ({time.time()-t0:.0f}s): {e}", flush=True)

elapsed = time.time() - t_start
print(f"[GPU {gpu_id}] COMPLETE: {ok} done, {skip} skipped, {fail} failed, {elapsed:.0f}s ({elapsed/60:.1f}min)", flush=True)
'''

WORKER_PATH = "/data/homework/RL/final2/rlfinal/_gpu_worker_4gpu.py"


def main():
    # Write worker script
    with open(WORKER_PATH, "w") as f:
        f.write(WORKER_SCRIPT)
    os.chmod(WORKER_PATH, 0o755)

    # Build task lists, round-robin across 4 GPUs
    task_queues = [[] for _ in range(N_GPUS)]
    gpu = 0
    for M, seed in product(M_VALUES, range(N_SEEDS)):
        for pipeline in ["ssl_dqn", "random_dqn"]:
            name = f"{pipeline}_M{M}_seed{seed}"
            task_queues[gpu].append((name, pipeline, M, seed))
            gpu = (gpu + 1) % N_GPUS

    for seed in range(N_SEEDS):
        name = f"compress_dqn_seed{seed}"
        task_queues[gpu].append((name, "compress_dqn", 16, seed))
        gpu = (gpu + 1) % N_GPUS

    for seed in range(N_SEEDS):
        name = f"identity_seed{seed}"
        task_queues[gpu].append((name, "identity", 64, seed))
        gpu = (gpu + 1) % N_GPUS

    # Write per-GPU task files
    for gid in range(N_GPUS):
        with open(f"/tmp/experiments_gpu{gid}.json", "w") as f:
            json.dump(task_queues[gid], f)

    # Print summary
    total = sum(len(q) for q in task_queues)
    max_per_gpu = max(len(q) for q in task_queues)
    est_min = max_per_gpu * 200 / 60
    print(f"Total experiments: {total}")
    for gid in range(N_GPUS):
        print(f"  GPU {gid}: {len(task_queues[gid])} experiments")
    print(f"Estimated wall time: ~{est_min:.0f} min ({est_min/60:.1f} h)")
    print()

    # Launch all 4 GPU workers in parallel
    procs = []
    for gid in range(N_GPUS):
        cmd = [sys.executable, "-u", WORKER_PATH, str(gid),
               f"/tmp/experiments_gpu{gid}.json", RESULTS_DIR]
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(gid)
        print(f"Launching GPU {gid} worker ({len(task_queues[gid])} tasks)...", flush=True)
        procs.append(subprocess.Popen(cmd, env=env,
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                      text=True, bufsize=1))

    # Stream interleaved output from all 4 workers
    t_total = time.time()
    poll_dict = {p.stdout: p for p in procs}
    while poll_dict:
        readable, _, _ = select.select(list(poll_dict.keys()), [], [], 10)
        for fd in readable:
            line = fd.readline()
            if line:
                print(line.rstrip(), flush=True)
            else:
                p = poll_dict.pop(fd)
                p.wait()

    t_total = time.time() - t_total
    n_ok = sum(1 for p in procs if p.returncode == 0)
    print(f"\n{'='*60}")
    print(f"All 4 GPU workers done in {t_total:.0f}s ({t_total/60:.1f} min)")
    print(f"Workers exited OK: {n_ok}/{N_GPUS}")
    print(f"Results: {RESULTS_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
