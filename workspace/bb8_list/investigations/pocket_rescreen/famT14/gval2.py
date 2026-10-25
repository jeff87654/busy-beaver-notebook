"""gval2.py M Q FJSON SEED [n] [topmark]: random macro-step validation of geng family F against literal sim.
Configs at a=0: borrows (with marks, blocks), leftmost R4 (multi-mark), R2. topmark=1 forces leftmost digit marked (P)."""
import sys, random, subprocess
from drv import SIM, show
from gk import gruns, gword
import json
import geng2 as G
enc, dec, macro = (lambda *a: G.enc(*a)), (lambda *a: G.dec(*a)), (lambda *a: G.macro(*a))
M, Q = sys.argv[1], sys.argv[2]; F = json.loads(sys.argv[3]); sys.argv[3:4] = ['x', 'x', 'x']
random.seed(int(sys.argv[6])); NT = int(sys.argv[7]) if len(sys.argv) > 7 else 200
def lit(ds, a, b, N=10**8):
    w = gword(enc(F, ds, a, b), F['z'])
    r = subprocess.run([SIM, M, '1', Q, w, str(len(w)), str(N), Q, '400'], capture_output=True, text=True).stdout.splitlines()
    for l in r:
        s = l.split(None, 2)
        if s[0] == 'H': return 'H'
        if s[0] != 'E' or len(s) < 3: continue
        runs, z = gruns(s[2])
        if z != F['z']: continue
        d = dec(F, runs)
        if d is not None and d[1] == 0 and len(d[0]) >= 1: return d
    return 'T'
cnt = {}; bad = []
for it in range(NT):
    kind = random.choice(['borrow', 'borrow', 'left', 'r2'])
    ds = []
    for _ in range(random.randint(1, 3)):
        L = random.randint(1, 10)
        ds += [(random.choice([0, 1, 1, 2]), 1)] + [(random.choice([0, 1, 1, 3, random.randint(0, 9)]), 0) for _ in range(L)]
    if random.random() < 0.5:
        ds += [(random.choice([0, 1, 2]), 1), (random.choice([0, 0, 3]), 0)] + [(random.choice([1, 2, 5]), 0) for _ in range(random.randint(1, 8))]
    ds[0] = (ds[0][0], 1); n = len(ds)
    if kind == 'left': ds = [(0, m) for v, m in ds]
    elif kind == 'borrow':
        k = random.randint(1, n - 1)
        for i in range(n - k, n): ds[i] = (0, ds[i][1])
        if all(v == 0 for v, _ in ds[:n - k]): ds[n - k - 1] = (random.randint(1, 3), ds[n - k - 1][1])
    else:
        ds[-1] = (random.randint(1, 6), 0)
    ds[-1] = (ds[-1][0], 0)
    if F['droptop'] and ds[0][0] > 0 and kind != 'r2': ds[0] = (0, 1)   # P is a value-0 marked digit in sep families
    if F['droptop']: ds[0] = (0, 1)
    if F['droptop'] and all(v == 0 for v, _ in ds[1:]) and kind == 'borrow': kind = 'left'
    b = len(ds) + random.randint(1, 60)
    exp = macro(F, ds, 0, b)
    got = lit(ds, 0, b)
    good = exp is not None and isinstance(got, tuple) and (got[0], got[2]) == (exp[0], exp[2])
    key = (kind, 'ok' if good else ('engine-invalid' if exp is None else 'BAD'))
    cnt[key] = cnt.get(key, 0) + 1
    if not good and exp is not None: bad.append((kind, show(enc(F, ds, 0, b))[:120], 'exp', show(enc(F, *exp))[:120], 'got', got if isinstance(got, str) else show(enc(F, *got))[:120]))
print(sorted(cnt.items()))
for x in bad[:4]: print(x)
