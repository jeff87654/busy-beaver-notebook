"""chain9.py: residue-level exhaustion chain for u-family (F1 rules) leaves whose even-A rebuild is P + (1,0)^m(A) + S; a'.
Uses resid.Eng mod M = 2^16; long block parts use the stabilised level maps (checked).  Prints the A residues at E1..E8."""
import idle, sys, re
import numpy as np
from resid import Eng
from ana2 import AS, po
M = 1 << 16; J = 700
E = Eng(M, J); ST = E.arr[J]
assert all((E.arr[j] == ST).all() for j in range(600, J + 1)), 'levels not stable'
def phi(j, x): return int(E.arr[min(j, J)][x])
def AE_struct(P, m, S, a):
    """A_E mod M for digits P + [1,0]*m + S (top first), m given exactly (int) possibly huge."""
    x = a % M; lev = 0
    for d in reversed(S):
        for _ in range(d): x = phi(lev, x)
        lev += 1
    # blocks (1,0) from the bottom: digit 0 at lev, digit 1 at lev+1
    done = 0
    while done < m and lev < 650:
        x = phi(lev + 1, x); lev += 2; done += 1
    if done < m:
        # stable region: block map is x -> ST[x]; iterate (m-done) times via orbit detection
        k = m - done; seen = {}; orb = []
        y = x
        while y not in seen and len(orb) < k: seen[y] = len(orb); orb.append(y); y = int(ST[y])
        if len(orb) == k: x = y
        else:
            t = seen[y]; p = len(orb) - t; x = orb[t + (k - t) % p] if k >= t else orb[k]
        lev += 2 * (m - done)
    for d in reversed(P):
        for _ in range(d): x = phi(lev, x)
        lev += 1
    return x
def fit(emap):
    """emap: {A: (ds, a)} for even A -> (P, S, alpha, beta, a')"""
    rec = {}
    for A, (ds, a) in emap.items():
        s = ','.join(map(str, ds)) + ','
        mt = re.match(r'^((?:\d+,)*?)((?:1,0,)+)((?:\d+,)*)$', s)
        P = [int(x) for x in mt[1].strip(',').split(',') if x]; m = len(mt[2]) // 4; S = [int(x) for x in mt[3].strip(',').split(',') if x]
        rec[A] = (tuple(P), tuple(S), m, a)
    As = sorted(rec); (P, S, m1, a1), (_, _, m2, _) = rec[As[0]], rec[As[1]]
    al = (m2 - m1) / (As[1] - As[0]); be = m1 - al * As[0]
    for A in As: assert rec[A][0] == P and rec[A][1] == S and rec[A][2] == al * A + be and rec[A][3] == a1, (A, rec[A])
    return list(P), list(S), al, be, a1
if __name__ == '__main__':
    fn, A1 = sys.argv[1], int(sys.argv[2])
    for l in open(fn):
        if l.startswith("#"): continue
        f = l.rstrip('\n').split('\t'); m_ = f[1]
        if len(sys.argv) > 3 and m_ not in sys.argv[3:]: continue
        em = {A: po(c) for A, c in zip(AS, f[3:])}
        ev = {A: (o[1], o[2]) for A, o in em.items() if o[0] == 'K' and A % 2 == 0}
        odd = set(o[0] for A, o in em.items() if A % 2 == 1)
        try: P, S, al, be, a1 = fit(ev)
        except Exception as ex: print(m_, 'fit failed', ex); continue
        A = A1; exact = True; seq = [A1]
        for step in range(8):
            if A % 2 == 1: seq.append('odd->' + '/'.join(odd)); break
            if exact: mm = int(al * A + be)
            else: mm = int((al * A + be)) % M + 4 * M     # residue representative, huge
            A = AE_struct(P, mm, S, a1); exact = False; seq.append(A)
        print(m_, f'P={P} m={al}A+{be} S={S} a={a1}', 'E-chain A mod 2^16:', seq)
