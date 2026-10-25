"""geng.py: generic family engine in T1 value units. state (ds [(v,mark)] top->bottom, a, b).
Family F = dict(B0, z, droptop, Q): encoding runs = [2v+m ...] + [2a, 2b+B0], trailing zeros z, head in state Q.
R1 phase: a -> 0, b += 2a.  R2: d1>0: d1-1, a=b+1, b=0.  R3: marked borrow (T1 rule).  R4: T1 rule; droptop: block top digit has value 0 (P stays M0)."""
from eng import borrow as t1borrow
def enc(F, ds, a, b):
    return [2 * v + m for v, m in ds] + [2 * a, 2 * b + F['B0']]
def dec(F, runs):
    if len(runs) < 3: return None
    A, B = runs[-2], runs[-1]
    if A % 2 or (B - F['B0']) % 2 or B < F['B0']: return None
    ds = [(r // 2, r % 2) for r in runs[:-2]]
    if ds and ds[-1][1]: return None
    return ds, A // 2, (B - F['B0']) // 2
def borrow(F, ds, b):
    r = t1borrow(ds, b)
    if r is None: return None
    out, a2, b2 = r
    if all(v == 0 for v, _ in ds) and F.get('droptop'):
        out = [(0, 1)] + out[1:]
    return out, a2, b2
def macro(F, ds, a, b):
    """from a=0 state: one R2 or R3/R4 then R1 phase -> next a=0 state"""
    if ds and ds[-1][0] > 0:
        ds = ds[:-1] + [(ds[-1][0] - 1, ds[-1][1])]; a, b = b + 1, 0
    else:
        r = borrow(F, ds, b)
        if r is None: return None
        ds, a, b = r
    return ds, 0, b + 2 * a
