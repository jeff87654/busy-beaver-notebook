"""val3: orbit-shaped probes: lists [M?, 1/0 block..., M, 0/vals, 12 low digits] with borrows over many zeros spanning marks,
and leftmost exhaustions of multi-mark lists (second-round R4). usage: val3.py SEED [-2]"""
import random, sys
from drv import *
from eng import *
M = T2 if '-2' in sys.argv else T1
random.seed(int(sys.argv[1]))
cnt = {}; bad = []
for it in range(120):
    nm = random.randint(1, 3)                     # number of blocks above the low part
    ds = []
    for _ in range(nm):
        L = random.randint(1, 12)
        ds += [(random.choice([0, 1, 1, 2]), 1)] + [(random.choice([0, 1, 1, 3]), 0) for _ in range(L)]
    low = random.randint(1, 13)
    ds += [(random.choice([0, 1, 2, 5]), 1), (random.choice([0, 0, 4]), 0)] + [(random.choice([1, 2, 7]), 0) for _ in range(low)]
    kind = random.choice(['borrow', 'borrow', 'left'])
    n = len(ds)
    if kind == 'left':
        ds = [(0, m) for v, m in ds]
    else:
        k = random.randint(2, n - 1)
        for i in range(n - k, n): ds[i] = (0, ds[i][1])
        if all(v == 0 for v, _ in ds[:n - k]): ds[n - k - 1] = (random.randint(1, 3), ds[n - k - 1][1])
    b = n + random.randint(1, 80)
    exp = step(ds, 0, b)
    if exp is None: cnt['invalid'] = cnt.get('invalid', 0) + 1; continue
    evs = nxt(to_runs(ds, 0, b), N=10**8, M=M, maxev=1)
    e = evs[0]
    got = e[0] if e[0] in ('H', 'T', 'TAPE') else from_runs(e[1])
    e0 = list(exp[0])
    while e0 and e0[0] == (0, 0): e0.pop(0)
    good = isinstance(got, tuple) and (got[0], got[1], got[2]) == (e0, exp[1], exp[2])
    cnt[(kind, good)] = cnt.get((kind, good), 0) + 1
    if not good: bad.append((kind, show(to_runs(ds, 0, b)), got if isinstance(got, str) else show(to_runs(*got))))
print(sorted(cnt.items(), key=str))
for x in bad[:5]: print(str(x)[:300])
