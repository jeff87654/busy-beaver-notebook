"""geng2.py: parametrized family engine (T1 rule shape). F keys:
 z (trailing zeros), A0,B0 (A-run = 2a+A0, B-run = 2b+B0), dl (digit run = 2v + (mark xor dl)),
 c2 (R2: a=b+c2), c3 (R3 top = b+c3-sum others), a3 (a after borrow/R4, b=0), c4 (R4 block R = b+c4-sum), droptop (R4 block top value 0)."""
def enc(F, ds, a, b):
    return [2 * v + (m ^ F['dl']) for v, m in ds] + [2 * a + F['A0'], 2 * b + F['B0']]
def dec(F, runs):
    if len(runs) < 3: return None
    A, B = runs[-2] - F['A0'], runs[-1] - F['B0']
    if A < 0 or B < 0 or A % 2 or B % 2: return None
    ds = []
    for r in runs[:-2]:
        m = (r % 2) ^ F['dl']; v = (r - (r % 2)) // 2
        if v < 0: return None
        ds.append((v, m))
    if ds and ds[-1][1]: return None
    return ds, A // 2, B // 2
def borrow(F, ds, b):
    j = max([i for i, (v, m) in enumerate(ds) if v > 0], default=-1)
    Z = ds[j + 1:]
    if not Z: return None
    new = [[None, Z[0][1]]] + [[0 if Z[t - 1][1] == 1 else 1, Z[t][1]] for t in range(1, len(Z))]
    if j >= 0:
        rem = b + F['c3'] - sum(x[0] for x in new[1:])
        if rem < 0: return None
        new[0][0] = rem
        out = ds[:j] + [(ds[j][0] - 1, ds[j][1])] + [tuple(x) for x in new]
    else:
        new[0][0] = 1
        R = b + F['c4'] - sum(x[0] for x in new)
        if R < 1: return None
        out = [(F.get('topv', 0 if F['droptop'] else 1), 1)] + [(1, 0)] * (R - 1) + [tuple(x) for x in new]
    return out, F['a3'], 0
def macro(F, ds, a, b):
    if ds and ds[-1][0] > 0:
        ds = ds[:-1] + [(ds[-1][0] - 1, ds[-1][1])]; a, b = b + F['c2'], 0
    else:
        r = borrow(F, ds, b)
        if r is None: return None
        ds, a, b = r
    return ds, 0, b + 2 * a
