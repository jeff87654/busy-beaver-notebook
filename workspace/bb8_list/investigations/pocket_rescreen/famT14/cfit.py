"""cfit.py: coding fit with validation. A coding passes if R2 sanity probes behave as d1-1 with b' = 2b+e (same e)."""
from ucode import detect, probe
import itertools
U = lambda v: (v, 0); Mk = lambda v: (v, 1)
SAN = [([Mk(1), U(2), U(3)], 30), ([Mk(1), U(2), U(3)], 31), ([Mk(1), U(3), U(1), U(2)], 40)]
def sane(C):
    es = set()
    for ds, b in SAN:
        o = probe(C, ds, b, N=2 * 10**6, maxev=600, tmo=5)
        if not o or o[0][0] in ('H', 'T'): return None
        out, bb = o[0]
        if out != ds[:-1] + [(ds[-1][0] - 1, 0)]: return None
        es.add(bb - 2 * b)
    return es.pop() if len(es) == 1 else None
def fit(M, Q, base=None):
    C0, why = (base, 'given') if base else detect(M, Q, 3000000)
    cands = []
    if C0: cands.append(C0)
    zs = [C0['z']] if C0 else [1, 2, 3]
    for z, A0, B0, dl in itertools.product(zs + [z for z in (1, 2, 3) if z not in zs], (0, 1, 2), (0, 1, 2, 3, 4), (0, 1)):
        C = dict(M=M, Q=Q, z=z, A0=A0, B0=B0, dl=dl)
        if C0 and C == C0: continue
        cands.append(C)
    for C in cands:
        e = sane(C)
        if e is not None: return C, e
    return None, why
