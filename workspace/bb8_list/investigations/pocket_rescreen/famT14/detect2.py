"""detect2.py: coding from blank-trace a=0 events + R2 pairs; validated by sanity probes (cfit.sane)."""
from collections import Counter
from ucode import events, chain_end
from cfit import sane
def detect2(M, Q, N=3000000):
    ev, tail = events(M, Q, N, maxev=6000)
    if len(ev) < 50: return None, 'few events (%d)' % len(ev)
    zc = Counter(e[2] for e in ev)
    for z, _ in zc.most_common(2):
        E = [e for e in ev if e[2] == z]
        ends = []
        for (s1, r1, _), (s2, r2, _) in zip(E, E[1:]):
            if len(r1) >= 3 and len(r2) == len(r1) and r1[:-2] == r2[:-2] and r2[-2] == r1[-2] - 1 and r2[-1] == r1[-1] + 2:
                ends.append(r2)
        if len(ends) < 10: continue
        A0 = Counter(r[-2] for r in ends).most_common(1)[0][0]
        Z = [r for r in ends if r[-2] == A0]
        # dedupe consecutive identical (chain interior)
        R2p = Counter(); par = Counter()
        for x, y in zip(Z, Z[1:]):
            if len(x) == len(y) and len(x) >= 3 and x[:-3] == y[:-3] and y[-3] == x[-3] - 2: R2p[x[-3] % 2] += 1
        for r in Z:
            for v in r[1:-3]: par[v % 2] += 1
        if not R2p: continue
        plo = R2p.most_common(1)[0][0]
        dl = 1 if par[1] > par[0] else 0
        lo = (plo - dl) % 2
        B0 = Counter(r[-1] % 2 for r in Z).most_common(1)[0][0]
        for A0x in (A0,):
            for dlx, lox in ((dl, lo), (1 - dl, (plo - (1 - dl)) % 2)):
                C = dict(M=M, Q=Q, z=z, A0=A0x, B0=B0, dl=dlx, lo=lox)
                e = sane(C)
                if e is not None: return C, e
                C['B0'] = B0 + 2
                e = sane(C)
                if e is not None: return C, e
    return None, 'no sane coding (z %s)' % dict(zc.most_common(3))
