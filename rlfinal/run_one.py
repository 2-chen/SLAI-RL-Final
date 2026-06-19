#!/usr/bin/env python3
import os, sys, json, time
sys.path.insert(0, "/data/homework/RL/final2")
from rlfinal.experiments.run_ssl_dqn import run_ssl_dqn, run_random_dqn, run_identity, run_compress_dqn

pipeline, M, seed, device, results_dir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
if pipeline == "compress_dqn":
    run_name = f"compress_dqn_d{M}_seed{seed}"
elif pipeline == "identity":
    run_name = f"identity_seed{seed}"
else:
    run_name = f"{pipeline}_M{M}_seed{seed}"
result_path = os.path.join(results_dir, f"{run_name}.json")
if os.path.exists(result_path):
    print(f"SKIP {run_name}")
    sys.exit(0)

print(f"START {run_name} on {device}")
t0 = time.time()
try:
    if pipeline == "ssl_dqn":
        run_ssl_dqn(M, seed, device, results_dir)
    elif pipeline == "random_dqn":
        run_random_dqn(M, seed, device, results_dir)
    elif pipeline == "compress_dqn":
        run_compress_dqn(seed, device, results_dir, bottleneck_dim=M)
    elif pipeline == "identity":
        run_identity(seed, device, results_dir)
    print(f"DONE  {run_name} ({time.time()-t0:.0f}s)")
except Exception as e:
    print(f"FAIL  {run_name}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)
