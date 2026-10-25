import sys, random
from rp import probe, vs
import eng34
row = int(sys.argv[1]); random.seed(5); ok = bad = 0; badl = []
tops = [(0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (7, 1)]
cases = []
for T in tops:
    for k in [0, 1, 2, 3, 4]:
        cases.append([T, (0, 1)] + [(0, 0)] * k)
        cases.append([T, (random.randint(1, 3), 1)] + [(0, 0)] * k)   # marked nonzero borrow
for v in [1, 2, 3, 4]:
    for m in [0, 1]: cases.append([(v, m)])
for ds in cases:
    b = len(ds) + random.randint(2, 30)
    exp = eng34.step(ds, b)
    strip = lambda d: d[next((i for i, x in enumerate(d) if x != (0, 0)), len(d)):]
    while exp is not None and not strip(exp[0]): exp = eng34.step(exp[0], exp[1])
    g = probe(row, ds, b, 1, N=3 * 10**8)
    want = '%s ;b=%d' % (vs(strip(exp[0])), exp[1])
    if g and g[0].split(': ', 1)[-1] == want: ok += 1
    else: bad += 1; badl.append((vs(ds), b, want, g[:1]))
print('row', row, 'targeted ok', ok, 'bad', bad); [print(x) for x in badl[:5]]
