"""val2: validate eng.step against literal sim. Lowest digit unmarked (invariant of real runs).
Mix: borrows over several zeros with marks, leftmost exhaustions, R1/R2 macro steps. usage: val2.py SEED [-2]"""
import random, sys
from drv import *
from eng import *
M = T2 if '-2' in sys.argv else T1
random.seed(int(sys.argv[1]))
cnt = {}; bad = []; inv = 0
for it in range(200):
    kind = random.choice(['borrow', 'borrow', 'left', 'r12'])
    n = random.randint(2, 10)
    ds = []
    for i in range(n):
        m = 1 if random.random() < 0.3 else 0
        v = random.choice([0, 1, 1, 2, 3, random.randint(0, 12)])
        ds.append((v, m))
    ds[0] = (ds[0][0], 1)
    if random.random() < 0.3:  # embed a block M1 1^r
        r = random.randint(1, 6); pos = random.randint(0, n - 1); ds[pos:pos] = [(1, 1)] + [(1, 0)] * (r - 1)
    n = len(ds)
    if kind == 'borrow':
        nz = random.randint(1, n - 1)
        for i in range(n - nz, n): ds[i] = (0, ds[i][1])
        if all(v == 0 for v, _ in ds[:n - nz]): ds[n - nz - 1] = (random.randint(1, 4), ds[n - nz - 1][1])
        a = 0
    elif kind == 'left':
        ds = [(0, m) for v, m in ds]; a = 0
    else:
        a = random.choice([0, random.randint(1, 15)])
        if ds[-1][0] == 0: ds[-1] = (random.randint(1, 9), 0)
    ds[-1] = (ds[-1][0], 0)
    b = random.randint(0, 45)
    exp = step(ds, a, b)
    if exp is None: inv += 1; continue
    evs = nxt(to_runs(ds, a, b), N=10**7, M=M, maxev=2 * a + 6)
    got = None
    for e in evs:
        if e[0] in ('H', 'T', 'TAPE'): got = e[0]; break
        g = from_runs(e[1])
        if g[1] == exp[1] and isinstance(g[2], int):
            got = g; break
    e0 = list(exp[0])
    while e0 and e0[0] == (0, 0): e0.pop(0)
    good = got not in (None, 'H', 'T', 'TAPE') and (got[0], got[1], got[2]) == (e0, exp[1], exp[2])
    cnt[(kind, good)] = cnt.get((kind, good), 0) + 1
    if not good: bad.append((kind, ds, a, b, exp, got))
print(sorted(cnt.items()), 'outside-validity', inv)
for x in bad[:5]: print(str(x)[:400])
