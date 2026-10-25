"""ILS over outlinings: start from Wade's outlining; kick = inline k random macros; re-outline with the
randomized exact-gain greedy; objective = full state count (incl. dechain + framework).
usage: python outl_ils.py CFG.json SECONDS SEED"""
import sys, time, random, pickle, outl, lowprio
cls, order = outl.load(sys.argv[1]); secs = float(sys.argv[2]); seed = int(sys.argv[3])
rng = random.Random(seed)
z = outl.fresh(cls, order); g0 = outl.G(z)
z.breakout_common_subsequences(); gw = outl.G(z)
def full(g):
    z = outl.fresh(cls, order); return outl.finish(outl.install(z, g))
best = gw; bv = full(gw); print('wade', bv, 'cells', gw.cells(), flush=True)
cur, cv = best, bv; t0 = time.time(); it = 0
while time.time() - t0 < secs:
    it += 1
    h = cur.copy(); esc = outl.escapes(h)
    ids = [v for v in h.s if v != h.root]
    k = rng.choice([1, 2, 3, 5, 8])
    for v in rng.sample(ids, min(k, len(ids))):
        if v in h.s: outl.inline(h, v, outl.escapes(h))
    h = outl.rgreedy_safe(h, rng, topT=rng.choice([20, 40]), noise=rng.choice([0.0, 1.0, 3.0]))
    v = full(h)
    if v <= cv:
        if v < bv:
            best, bv = h, v; print(it, 'states', v, 'cells', h.cells(), f't={time.time()-t0:.0f}', flush=True)
            pickle.dump(h.s, open(sys.argv[1] + f'.ils{seed}.pkl', 'wb'))
        cur, cv = h, v
    elif rng.random() < 0.05:
        cur, cv = best, bv
print('iters', it, 'best', bv)
