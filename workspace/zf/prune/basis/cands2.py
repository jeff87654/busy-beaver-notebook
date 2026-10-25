"""Faster candidate filter: bottom-up enumeration of C/N formulas over p,q,r with 8-bit truth tables;
only tautologies of exactly K connectives are matrix-checked (vectorized over all filter matrices).
KEEP = axioms kept beside Y (comma list of B1,B2,B3); Y must refute every MP-closed 3-valued matrix that
validates the kept axioms but fails one of B1-B3.  usage: python cands2.py K KEEP"""
import sys, pickle, itertools
import numpy as np
sys.path.insert(0, '..'); import lowprio  # noqa
K = int(sys.argv[1]); KEEP = sys.argv[2]
idx = {'B1': 3, 'B2': 4, 'B3': 5}
mats = [m for m in pickle.load(open('mats3all.pkl', 'rb')) if all(m[idx[k]] for k in KEEP.split(','))]
I = np.array([m[0] for m in mats], dtype=np.int8); Nn = np.array([m[1] for m in mats], dtype=np.int8)
D = np.array([[v in m[2] for v in range(3)] for m in mats]); M = len(mats); Mi = np.arange(M)[:, None]
asg = np.array(list(itertools.product(range(3), repeat=3)), dtype=np.int8)   # 27 x 3
print(KEEP, 'filter matrices', M, file=sys.stderr, flush=True)
P, Q, R = 0b11110000, 0b11001100, 0b10101010
def show(t):
    if isinstance(t, int): return 'pqr'[t]
    return t[0] + ''.join(show(x) for x in t[1:])
def ev(t):
    if isinstance(t, int): return np.broadcast_to(asg[:, t][None, :], (M, 27))
    if t[0] == 'N': return Nn[Mi, ev(t[1])]
    return I[Mi, ev(t[1]), ev(t[2])]
def canon(t, m=None):
    if m is None: m = {}
    if isinstance(t, int):
        if t not in m: m[t] = len(m)
        return m[t]
    return (t[0],) + tuple(canon(x, m) for x in t[1:])
lev = [[(0, P), (1, Q), (2, R)]]
for k in range(1, K):
    L = [(('N', a), (~ta) & 255) for a, ta in lev[k - 1]]
    for i in range(k):
        for a, ta in lev[i]:
            for b, tb in lev[k - 1 - i]:
                L.append((('C', a, b), ((~ta) | tb) & 255))
    lev.append(L); print('level', k, len(L), file=sys.stderr, flush=True)
seen = set(); surv = []; ntaut = 0
def consider(t):
    global ntaut
    c = canon(t)
    if c in seen: return
    seen.add(c); ntaut += 1
    if not D[Mi, ev(c)].all(axis=1).any():
        surv.append(c); print(K, show(c), flush=True)
for a, ta in lev[K - 1]:
    if (~ta) & 255 == 255: consider(('N', a))
for i in range(K):
    for a, ta in lev[i]:
        for b, tb in lev[K - 1 - i]:
            if ((~ta) | tb) & 255 == 255: consider(('C', a, b))
pickle.dump(surv, open(f'surv2_{K}_{KEEP}.pkl', 'wb'))
print('tautologies', ntaut, 'survivors', len(surv), file=sys.stderr)
