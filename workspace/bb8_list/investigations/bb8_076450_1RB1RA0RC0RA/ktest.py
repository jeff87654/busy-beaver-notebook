import sys, itertools, random
from kfam import run_next, predict
random.seed(1)
cases = []
for n in range(0, 4):
    for ds in itertools.product(range(0, 4), repeat=n):
        if ds and ds[0] == 0: continue
        for a in range(0, 3):
            for b in range(0, 6):
                cases.append((ds, a, b))
bad = 0; tot = 0; halts = []
for ds, a, b in cases:
    r = run_next(ds, a, b, N=10**6)
    p = predict(ds, a, b)
    tot += 1
    if r[0] != 'K' or r[2] != p:
        bad += 1
        if bad <= 60: print('MISMATCH', (ds, a, b), 'pred', p, 'got', r)
print('total', tot, 'bad', bad)
