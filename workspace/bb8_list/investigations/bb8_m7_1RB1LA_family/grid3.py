import random, sys
from grid2 import predict, literal
from kd import TM
random.seed(7)
tm = sys.argv[1] if len(sys.argv) > 1 else TM
bad = tot = 0
for _ in range(1500):
    n = random.randint(1, 6)
    ds = [random.choice([1, 2, 3, 4, 5, 0, 0, 0]) for _ in range(n)]
    while ds and ds[0] == 0: ds = ds[1:]
    if not ds: continue
    b = random.randint(1, 16)
    a = 0 if random.random() < 0.8 else random.randint(1, 3)
    k = random.randint(0, 14)
    ds = tuple(ds) + (0,) * k
    p = predict(ds, a, b); l = literal(tm, ds, a, b, N=4 * 10**6)
    tot += 1
    if l[0] != 'K' or l[1] != p:
        bad += 1
        if bad < 6: print('MISMATCH', ds, a, b, p, l[:2])
print(tm, tot, 'random cases,', bad, 'mismatches')
