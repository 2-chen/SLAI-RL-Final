#!/usr/bin/env python3
"""Launch experiments: 2 GPU workers, each sequential, zero CUDA contention."""
import os, sys, subprocess, time, json
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

M_VALUES = [128, 256, 512, 1024]
N_SEEDS = 20
RESULTS_DIR = "/data/homework/RL/final2/results"

# ============================================================================
# Per-GPU worker: runs experiments sequentially on its assigned GPU
# ============================================================================
WORKER = '''#!/usr/bin/env python3 -u
import os, sys, json, time, traceback
os.environ["CUDA_VISIBLE_DEVICES"] = sys.argv[1]
gpu_id = sys.argv[1]
sys.path.insert(0, "/data/homework/RL/final2")
from rlfinal.experiments.run_ssl_dqn import run_ssl_dqn, run_random_dqn, run_identity, run_compress_dqn

tasks_file = sys.argv[2]
results_dir = sys.argv[3]
tasks = json.loads(open(tasks_file).read())

print(f"[GPU {gpu_id}] {len(tasks)} experiments queued", flush=True)
t_start = time.time()
ok = 0
skip = 0
fail = 0

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
        eta = elapsed * (len(tasks) - i - 1)
        print(f"[GPU {gpu_id}] [{i+1}/{len(tasks)}] {name} DONE ({elapsed:.0f}s) ETA:{eta/60:.0f}min", flush=True)
    except Exception as e:
        fail += 1
        traceback.print_exc()
        print(f"[GPU {gpu_id}] [{i+1}/{len(tasks)}] {name} FAIL ({time.time()-t0:.0f}s): {e}", flush=True)

elapsed = time.time() - t_start
print(f"[GPU {gpu_id}] COMPLETE: {ok} done, {skip} skipped, {fail} failed, {elapsed:.0f}s ({elapsed/60:.1f}min)", flush=True)
'''

WORKER_PATH = "/data/homework/RL/final2/rlfinal/_gpu_worker.py"

# ============================================================================
def main():
    # Write worker script
    with open(WORKER_PATH, "w") as f:
        f.write(WORKER)
    os.chmod(WORKER_PATH, 0o755)

    # Build task lists, round-robin across GPUs
    tasks_gpu0, tasks_gpu1 = [], []
    gpu = 0
    for M, seed in product(M_VALUES, range(N_SEEDS)):
        for pipeline in ["ssl_dqn", "random_dqn"]:
            name = f"{pipeline}_M{M}_seed{seed}"
            (tasks_gpu0 if gpu == 0 else tasks_gpu1).append((name, pipeline, M, seed))
            gpu = (gpu + 1) % 2

    for seed in range(N_SEEDS):
        name = f"compress_dqn_seed{seed}"
        (tasks_gpu0 if gpu == 0 else tasks_gpu1).append((name, "compress_dqn", 16, seed))
        gpu = (gpu + 1) % 2

    for seed in range(N_SEEDS):
        name = f"identity_seed{seed}"
        (tasks_gpu0 if gpu == 0 else tasks_gpu1).append((name, "identity", 64, seed))
        gpu = (gpu + 1) % 2

    # Write task files
    for gid, tasks in [(0, tasks_gpu0), (1, tasks_gpu1)]:
        with open(f"/tmp/experiments_gpu{gid}.json", "w") as f:
            json.dump(tasks, f)

    # Rough estimate: ~200s/experiment avg
    est_min = max(len(tasks_gpu0), len(tasks_gpu1)) * 200 / 60
    print(f"GPU 0: {len(tasks_gpu0)} experiments")
    print(f"GPU 1: {len(tasks_gpu1)} experiments")
    print(f"Estimated wall time: ~{est_min:.0f} min ({est_min/60:.1f} h)")
    print()

    # Launch both GPU workers
    procs = []
    for gpu_id in [0, 1]:
        cmd = [sys.executable, "-u", WORKER_PATH, str(gpu_id), f"/tmp/experiments_gpu{gpu_id}.json", RESULTS_DIR]
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
        print(f"Launching GPU {gpu_id} worker ({len(tasks_gpu0 if gpu_id==0 else tasks_gpu1)} tasks)...", flush=True)
        procs.append(subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1))

    # Stream output from both workers interleaved
    import select
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
    print(f"\nAll done in {t_total:.0f}s ({t_total/60:.1f} min)")
    print(f"Workers OK: {n_ok}/2")
    os.unlink(WORKER_PATH)

if __name__ == "__main__":
    main()
