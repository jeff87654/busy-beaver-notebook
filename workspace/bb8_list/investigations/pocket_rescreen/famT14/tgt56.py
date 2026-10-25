import sys, random
from rp56 import probe, vs
import eng56
row = int(sys.argv[1]); random.seed(9); ok = bad = 0; badl = []
for it in range(60):
    top = [(random.randint(1, 5), 1)] + [(random.choice([0, 1, 2, 4]), random.choice([0, 1])) for _ in range(random.randint(0, 3))]
    k = random.randint(1, 5)
    ds = top + [(0, 1)] + [(0, 0)] * k
    if random.random() < 0.3: ds = top + [(0, 1), (0, 1)] + [(0, 0)] * k
    b = len(ds) + random.randint(0, 40)
    exp = eng56.step(ds, b)
    g = probe(row, ds, b, 1, N=3 * 10**8); g = g[0] if g else 'none'
    want = '%s ;b=%d' % (vs(eng56.norm(exp[0])), exp[1])
    if g.split(': ', 1)[-1] == want: ok += 1
    else: bad += 1; badl.append((vs(ds), b, want, g))
print('row', row, 'RM targeted ok', ok, 'bad', bad); [print(x) for x in badl[:4]]
