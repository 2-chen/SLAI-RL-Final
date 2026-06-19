#!/usr/bin/env python3 -u
import os, sys, json, time, traceback
gpu_id = sys.argv[1]
os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
sys.path.insert(0, "/data/homework/RL/final2")
from rlfinal.experiments.run_ssl_dqn import run_ssl_dqn, run_random_dqn, run_identity

tasks_file = sys.argv[2]
results_dir = sys.argv[3]
tasks = json.loads(open(tasks_file).read())

print(f"[GPU {gpu_id}] {len(tasks)} experiments queued", flush=True)
t_start = time.time()
ok = skip = fail = 0

for i, task in enumerate(tasks):
    name, pipeline, M, seed = task
    rname = f"{pipeline}_M{M}_seed{seed}" if pipeline != "identity" else f"identity_seed{seed}"
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
