import sys, random
from rp56 import probe, vs
import eng56
row = int(sys.argv[1]); random.seed(int(sys.argv[2])); NT = int(sys.argv[3])
cnt = {}; bad = []
for it in range(NT):
    n = random.randint(1, 7)
    ds = [(random.choice([0, 0, 1, 1, 2, 3, random.randint(0, 9)]), 1 if random.random() < 0.35 else 0) for _ in range(n)]
    ds[0] = (max(ds[0][0], 1), 1)
    kind = random.choice(['R2', 'zeros', 'zeros', 'low'])
    if kind == 'R2': ds[-1] = (random.randint(1, 5), random.choice([0, 1]))
    elif kind == 'zeros':
        k = random.randint(1, 5); ds += [(0, 0)] * k
        if random.random() < 0.25: ds = [(0, 0)] * k
    else: ds[-1] = (0, 1)
    b = len(ds) + random.randint(0, 40)
    exp = eng56.step(ds, b)
    if exp is None: cnt['inv'] = cnt.get('inv', 0) + 1; continue
    g = probe(row, ds, b, 1, N=3 * 10**8)
    g = g[0] if g else 'none'
    want = '%s ;b=%d' % (vs(eng56.norm(exp[0])), exp[1])
    got = g.split(': ', 1)[-1]
    ok = got == want
    key = (exp[2], 'ok' if ok else 'BAD'); cnt[key] = cnt.get(key, 0) + 1
    if not ok: bad.append((vs(ds), b, exp[2], want[:70], g[:70]))
print('row', row, sorted(cnt.items(), key=str))
for x in bad[:6]: print(x)
