"""val34.py ROW SEED N: random macro probes of eng34 vs literal."""
import sys, random
from rp import probe, vs
import eng34
row = int(sys.argv[1]); random.seed(int(sys.argv[2])); NT = int(sys.argv[3])
cnt = {}; bad = []
for it in range(NT):
    n = random.randint(1, 8)
    ds = [(random.choice([0, 0, 1, 1, 2, 3, random.randint(0, 9)]), 1 if random.random() < 0.35 else 0) for _ in range(n)]
    if random.random() < 0.5: ds = [(0, 1)] + ds
    kind = random.choice(['R2', 'zeros', 'zeros', 'low'])
    if kind == 'R2': ds[-1] = (random.randint(1, 5), random.choice([0, 0, 1]))
    elif kind == 'zeros':
        k = random.randint(1, 5); ds += [(0, 0)] * k
        if random.random() < 0.2: ds = [(0, 0)] * k
    else: ds[-1] = (0, 1)
    b = len(ds) + random.randint(0, 40)
    exp = eng34.step(ds, b)
    got = probe(row, ds, b, 1, N=3 * 10**8)
    g = got[0] if got else 'none'
    if exp is None: key = (kind, 'engine-invalid'); cnt[key] = cnt.get(key, 0) + 1; continue
    # literal decode drops leading unmarked zero digits
    e0 = list(exp[0])
    while e0 and e0[0] == (0, 0): e0.pop(0)
    want = '%s ;b=%d' % (vs(e0), exp[1])
    ok = g.split(': ', 1)[-1] == want
    key = (exp[2], 'ok' if ok else 'BAD'); cnt[key] = cnt.get(key, 0) + 1
    if not ok: bad.append((vs(ds), b, exp[2], 'exp', want[:80], 'got', g[:80]))
print(sorted(cnt.items()))
for x in bad[:6]: print(x)
