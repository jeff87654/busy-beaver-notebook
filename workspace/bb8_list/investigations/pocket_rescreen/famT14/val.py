import random, sys
from drv import *
from eng import *
M = T2 if '-2' in sys.argv else T1
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] != '-2' else 1)
ok = bad = inv = 0; badl = []
for it in range(150):
    n = random.randint(1, 9)
    ds = []
    for i in range(n):
        m = 1 if random.random() < 0.3 else 0
        v = random.choice([0, 0, 0, 1, 1, 2, 3, random.randint(0, 9)])
        ds.append((v, m))
    if random.random() < 0.8: ds[0] = (ds[0][0], 1)   # leftmost usually marked
    nz = random.randint(0, n)                         # force trailing zeros
    for i in range(n - nz, n): ds[i] = (0, ds[i][1])
    if random.random() < 0.7: ds[-1] = (ds[-1][0], 0)  # lowest usually unmarked
    b = random.randint(0, 40); a = 0
    exp = step(ds, a, b)
    ev = nxt(to_runs(ds, a, b), N=10**7, M=M, maxev=1)[0]
    if ev[0] in ('H', 'T', 'TAPE'): got = ev[0]
    else: got = from_runs(ev[1])
    if exp is None:
        inv += 1; continue
    # literal parse drops leading zero digits (tape starts at leftmost 1); compare modulo leading unmarked zeros
    e2 = list(exp); e0 = list(e2[0])
    while e0 and e0[0] == (0, 0): e0.pop(0)
    if got != 'H' and got != 'T' and got != 'TAPE' and (got[0], got[1], got[2]) == (e0, e2[1], e2[2]): ok += 1
    else:
        bad += 1; badl.append((ds, b, exp, got))
print('ok', ok, 'bad', bad, 'outside-validity', inv)
for x in badl[:8]: print(x)
