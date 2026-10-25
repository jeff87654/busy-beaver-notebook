"""lock2: lockstep literal vs micro-engine from an arbitrary K-config; counts R4 (leftmost rebuild) events + min margins.
usage: lock2.py 'DS' a b NSTEPS MAXEV [-2]   (DS like 'M1 1^2')"""
import sys
from drv import *
from eng import *
M = T2 if '-2' in sys.argv else T1
ds0 = [(x // 2, x % 2) for x in parse_ds(sys.argv[1])]; a0, b0 = int(sys.argv[2]), int(sys.argv[3])
N, maxev = int(sys.argv[4]), int(sys.argv[5])
K = []; last = ''
for L in run(rword(to_runs(ds0, a0, b0)), N, maxev, M):
    p = L.split(None, 2)
    if p[0] == 'E':
        r = toruns(p[2])
        if len(r) >= 3:
            k = from_runs(r)
            if isinstance(k[1], int) and isinstance(k[2], int): K.append((int(p[1]), k))
    else: last = L
st = (ds0, a0, b0); ok = 0; mism = None; r4 = []; minm = None
for s, k in K:
    ds, a, b = st
    if a > 0: st = (ds, a - 1, b + 2)
    else:
        if not (ds and ds[-1][0] > 0):
            j = max([i for i, (v, m) in enumerate(ds) if v > 0], default=-1)
            kz = len(ds) - 1 - j
            marg = b - kz - 1
            minm = marg if minm is None else min(minm, marg)
            if j < 0: r4.append((s, len(ds), b))
        st = step(ds, a, b)
    if st is None: mism = ('engine-invalid', s); break
    e0 = list(st[0])
    while e0 and e0[0] == (0, 0): e0.pop(0)
    if (e0, st[1], st[2]) != (list(k[0]), k[1], k[2]):
        mism = (s, show(to_runs(*st))[:100], show(to_runs(*k))[:100]); break
    ok += 1
print('K', len(K), 'lockstep ok', ok, 'mismatch', mism, '| literal end:', last[:40])
print('R4 events (step, N digits, b):', r4[:10], 'min margin b-k-1 at borrows:', minm)
if K: print('last', K[-1][0], show(to_runs(*K[-1][1]))[:150])
