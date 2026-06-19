import json, os, glob, numpy as np
from collections import defaultdict

results_dir = '/data/homework/RL/final2/results'
data = defaultdict(list)

for fpath in glob.glob(os.path.join(results_dir, '*.json')):
    with open(fpath) as f:
        r = json.load(f)
    pipeline = r['pipeline']
    M = r.get('M', 64)
    seed = r['seed']

    sr = r.get('eval_success_rates', [])
    final_sr = sr[-1][1] if sr else 0
    returns = [v for _, v in r.get('eval_avg_returns', [])]
    final_return = returns[-1] if returns else 0
    path_lens = [v for _, v in r.get('eval_avg_path_lengths', [])]
    final_path = path_lens[-1] if path_lens else 64

    def episodes_to_threshold(curve, threshold=0.9):
        for ep, val in curve:
            if val >= threshold:
                return ep
        return 1000

    ep90 = episodes_to_threshold(sr)

    key = (pipeline, M)
    data[key].append({
        'seed': seed, 'final_sr': final_sr, 'final_return': final_return,
        'final_path': final_path, 'ep90': ep90,
        'ssl_final_loss': r.get('ssl_final_loss', None)
    })

print('Pipeline & M & Episodes to 90% & Final SR & Final Return & Final Path Len \\\\')
print('\\midrule')
for pipeline in ['identity', 'ssl_dqn', 'random_dqn', 'compress_dqn']:
    for M in [64, 128, 256, 512, 1024, 16]:
        key = (pipeline, M)
        if key not in data:
            continue
        vals = data[key]
        ep90s = [v['ep90'] for v in vals]
        srs = [v['final_sr'] for v in vals]
        rets = [v['final_return'] for v in vals]
        paths = [v['final_path'] for v in vals]

        pipe_label = {'identity': 'Identity', 'ssl_dqn': 'SSL->DQN', 'random_dqn': 'DQN-only', 'compress_dqn': 'Compress->DQN'}[pipeline]
        M_label = '---' if pipeline in ('identity', 'compress_dqn') else str(M)
        print(f'{pipe_label} & {M_label} & {np.mean(ep90s):.0f}$\\pm${np.std(ep90s):.0f} & {np.mean(srs):.2f}$\\pm${np.std(srs):.2f} & {np.mean(rets):.2f}$\\pm${np.std(rets):.2f} & {np.mean(paths):.1f}$\\pm${np.std(paths):.1f} \\\\')

print()
print('Path length analysis:')
for pipeline in ['identity', 'ssl_dqn', 'random_dqn', 'compress_dqn']:
    for M in [64, 128, 256, 512, 1024, 16]:
        key = (pipeline, M)
        if key not in data:
            continue
        paths = [v['final_path'] for v in data[key]]
        optimal = sum(1 for p in paths if p <= 15)
        print(f'{pipeline} M={M}: path={np.mean(paths):.1f}, optimal_rate={optimal}/{len(paths)}')

print()
print('SSL Reconstruction Loss:')
for M in [128, 256, 512, 1024]:
    losses = [v['ssl_final_loss'] for v in data[('ssl_dqn', M)]]
    print(f'M={M}: loss={np.mean(losses):.6f} +- {np.std(losses):.6f}')
