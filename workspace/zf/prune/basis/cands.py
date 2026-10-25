"""Enumerate candidate axioms Y (C/N formulas over p,q,r, at most K connectives), keep tautologies, and
filter with the 3-valued matrices: {B1, Y} can only be complete if no B1-valid matrix where B2 or B3
fails validates Y."""
import sys, itertools, pickle
import numpy as np
sys.path.insert(0, '..'); import lowprio  # noqa
K = int(sys.argv[1]); NV = 3
KEEP = sys.argv[2] if len(sys.argv) > 2 else 'B1'   # axioms kept besides Y
def forms(k):  # formulas with exactly k connectives
    if k == 0:
        for v in range(NV): yield v
        return
    for a in forms(k - 1): yield ('N', a)
    for i in range(k):
        for a in forms(i):
            for b in forms(k - 1 - i): yield ('C', a, b)
def vars_(t): return {t} if isinstance(t, int) else set().union(*(vars_(x) for x in t[1:]))
def canon(t):
    m = {}
    def go(t):
        if isinstance(t, int):
            if t not in m: m[t] = len(m)
            return m[t]
        return (t[0],) + tuple(go(x) for x in t[1:])
    return go(t)
def show(t):
    if isinstance(t, int): return 'pqr'[t]
    return t[0] + ''.join(show(x) for x in t[1:])
def taut(t):
    vs = sorted(vars_(t))
    for bits in itertools.product((0, 1), repeat=len(vs)):
        env = dict(zip(vs, bits))
        def ev(t):
            if isinstance(t, int): return env[t]
            if t[0] == 'N': return 1 - ev(t[1])
            return int((not ev(t[1])) or ev(t[2]))
        if not ev(t): return False
    return True
import random
idx = {'B1': 3, 'B2': 4, 'B3': 5}
allm = [m for m in pickle.load(open('mats3all.pkl', 'rb')) if all(m[idx[k]] for k in KEEP.split(','))]
random.seed(1); random.shuffle(allm)
def arrs(mats):
    return (np.array([m[0] for m in mats], dtype=np.int8), np.array([m[1] for m in mats], dtype=np.int8),
            np.array([[v in m[2] for v in range(3)] for m in mats]), np.arange(len(mats)))
SMALL = arrs(allm[:300]); FULL = arrs(allm)
mats = allm
Iarr = np.array([m[0] for m in mats], dtype=np.int8)       # (M,3,3)
Narr = np.array([m[1] for m in mats], dtype=np.int8)       # (M,3)
Darr = np.array([[v in m[2] for v in range(3)] for m in mats])  # (M,3)
Mi = np.arange(len(mats))
print(KEEP, 'filter matrices:', len(mats), file=sys.stderr)
def valid_mask(t, A=None):
    Iarr, Narr, Darr, Mi = A
    vs = sorted(vars_(t)); ok = np.ones(len(Mi), bool)
    for vals in itertools.product(range(3), repeat=len(vs)):
        env = dict(zip(vs, vals))
        def ev(t):
            if isinstance(t, int): return np.full(len(Mi), env[t], np.int8)
            if t[0] == 'N': return Narr[Mi, ev(t[1])]
            return Iarr[Mi, ev(t[1]), ev(t[2])]
        ok &= Darr[Mi, ev(t)]
    return ok
seen = set(); surv = []
for k in range(1, K + 1):
    for t in forms(k):
        c = canon(t)
        if c in seen: continue
        seen.add(c)
        if not taut(c): continue
        if valid_mask(c, SMALL).any() or valid_mask(c, FULL).any(): continue
        surv.append(c); print(k, show(c), flush=True)
pickle.dump(surv, open(f'surv{K}_{KEEP}.pkl', 'wb'))
print('survivors', len(surv), file=sys.stderr)
