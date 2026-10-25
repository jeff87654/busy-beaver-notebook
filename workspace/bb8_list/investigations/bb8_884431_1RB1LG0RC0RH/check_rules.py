"""Exact literal check of the digit-list rules R1-R4 of 1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA
(mirror machine, kfam shape A,10; b' = 2b+1 is the run length).  python check_rules.py [TM_actual]"""
import sys, itertools
from common import *
if len(sys.argv) > 1 and '_' in sys.argv[1]:
    MIR = mirror(sys.argv[1])
def kz(ds): return trailing_zeros(ds)
def predict(ds, a, b):
    ds = list(ds)
    if a >= 1: return ('K', (tuple(ds), a - 1, b + 1))
    k = kz(ds)
    if k == len(ds):
        if b == 0: return None
        return ('K', ((4,) + (2,) * (b - 1), 2, 0))
    i = len(ds) - 1 - k
    if k == 0:
        if b == 0: return None
        ds[-1] -= 1
        return ('K', (strip(ds), 2 * b + 2, 0))
    if k < b:
        ds[i] -= 1
        ds = ds[:i + 1] + [2 * (b + 1 - k)] + [2] * (k - 1)
        return ('K', (strip(ds), 2, 0))
    return None
def main():
    stats = {}; bad = []
    cases = []
    for n in range(0, 4):
        for ds in itertools.product(range(0, 4), repeat=n):
            if ds and ds[0] == 0: continue
            for a in range(0, 4):
                for b in range(0, 6):
                    cases.append((ds, a, b))
    for b in range(0, 9):
        for k in range(1, b + 6):
            for y in (1, 2):
                cases.append(((1, y) + (0,) * k, 0, b))
    for ds, a, b in cases:
        r = run_next(MIR, ds, a, 2 * b + 1, N=10**6)
        p = predict(ds, a, b)
        kind = 'R1' if a else ('R4' if kz(ds) == len(ds) else ('R2' if kz(ds) == 0 else 'R3'))
        if p is None:
            kind = 'unpred'
            stats.setdefault(kind, [0, 0]); stats[kind][0] += 1
            continue
        got = ('K', (r[2][0], r[2][1], (r[2][2] - 1) // 2)) if r[0] == 'K' else (r[0],)
        # R1 with ds empty and a = 1 may be followed immediately by nothing special: first K config is the prediction
        ok = got == ('K', (tuple(p[1][0]), p[1][1], p[1][2]))
        stats.setdefault(kind, [0, 0]); stats[kind][0] += 1; stats[kind][1] += ok
        if not ok: bad.append((kind, (ds, a, b), got, p))
    print({k: '%d/%d' % (v[1], v[0]) for k, v in stats.items()})
    for x in bad[:20]: print('MISMATCH', x)

if __name__ == '__main__':
    main()
