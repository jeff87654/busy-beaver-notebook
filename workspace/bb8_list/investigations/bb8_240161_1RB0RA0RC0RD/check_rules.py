"""Check the K-family rules of the mirror machine against exact literal simulation, including b=0 and k>=b."""
import os, sys, itertools
os.environ['BB_KENC'] = '10,0'
from kfam import run_next, set_shape, show, trailing_zeros, strip
set_shape('E', '11')
TM = '1LB0LA_0LC0LD_0RD---_1LE0RF_1LF1LD_1RE0RG_1RF1RH_0LA0RG'

def predict(ds, a, b):
    ds = list(ds)
    if a >= 1:
        if not ds and a == 1:
            return predict(ds, 0, b + 2)
        return ('K', (tuple(ds), a - 1, b + 2))
    k = trailing_zeros(ds)
    if k == len(ds):
        if b < 1: return None
        return ('K', (strip((2,) + (1,) * (b - 1)), 1, 0))
    i = len(ds) - 1 - k
    if k == 0:
        if b == 0:
            return ('HALT',)   # R2 with b = 0 halts (never reached: b >= 2 at every reset)
        ds[-1] -= 1
        return ('K', (strip(ds), b + 2, 0))
    if k < b:
        ds[i] -= 1
        ds = ds[:i + 1] + [b + 2 - k] + [1] * (k - 1)
        return ('K', (strip(ds), 1, 0))
    if k == b:
        return ('HALT',)
    return None

def kind(ds, a, b):
    if a >= 1: return 'R1'
    k = trailing_zeros(ds)
    if k == len(ds): return 'R4'
    if k == 0: return 'R2'
    return 'R3' if k < b else ('HALT' if k == b else 'R3big')

def grid():
    for n in range(0, 4):
        for ds in itertools.product(range(0, 4), repeat=n):
            if ds and ds[0] == 0: continue
            for a in range(0, 4):
                for b in range(0, 6):
                    yield (ds, a, b)
    for b in range(0, 9):
        for k in range(1, b + 6):
            for y in (1, 2):
                yield ((1, y) + (0,) * k, 0, b)

st = {}; bad = []; other = {}
for ds, a, b in grid():
    r = run_next(TM, ds, a, b, N=10 ** 6)
    got = ('K', r[2]) if r[0] == 'K' else (r[0],)
    p = predict(ds, a, b)
    kd = kind(ds, a, b)
    if kd in ('R1', 'R2', 'R3', 'HALT', 'R4') and p is None: kd += '?'
    ok = p is None or got == p
    st.setdefault(kd, [0, 0]); st[kd][0] += 1; st[kd][1] += ok
    if not ok: bad.append((kd, ds, a, b, got, p))
    if p is None: other.setdefault(kd, []).append(((ds, a, b), got if got[0] != 'K' else show(got[1])))
print({k: tuple(v) for k, v in st.items()})
for x in bad[:20]: print('BAD', x)
for kd, l in other.items():
    print(kd, len(l)); 
    for x in l[:12]: print('   ', x)
