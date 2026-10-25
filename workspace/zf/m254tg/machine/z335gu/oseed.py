"""Min state count over random outliner tie-breaking seeds for a fixed config.
usage: python oseed.py CFG.json N"""
import sys, json, time, collections
import lowprio, zfp
cfg = json.load(open(sys.argv[1])); N = int(sys.argv[2])
perm = {k: tuple(v) for k, v in cfg.get('perm', {}).items()}
def cost(seed):
    return zfp.cost(zfp.make(cfg['clauses'], perm, cfg['opt'], cfg.get('vmap', {}), cfg.get('flips', {}), oseed=seed), cfg['order'])
t = time.time(); base = cost(None); print('wade', base, f'{time.time()-t:.2f}s', flush=True)
hist = collections.Counter(); best = (base, None)
for s in range(N):
    c = cost(s); hist[c] += 1
    if c < best[0]: best = (c, s); print('seed', s, c, flush=True)
print('hist', sorted(hist.items())[:10], 'best', best)
