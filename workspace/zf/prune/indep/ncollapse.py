"""Name-dependent collapsed matrices.  Variable 9 is 'special', all others 'normal'.  A. x a := Qs(a) if
x = 9 else Qn(a).  An atom's value depends on its pattern (kind of left var, kind of right var, same?).
ZF axioms only contain normal variables in distinct-variable atoms.  Searches a countermodel for each
target among B4 B6a B6b B6c B7 B8a B8b B8c."""
import sys, itertools
sys.path.insert(0, '..'); import lowprio  # noqa
from collapse import EXT, POW, UNI, INF, REP, PH, ev as cev

VARS = (0, 1, 2, 9)
PATS = [('n','n',False), ('n','n',True), ('n','s',False), ('s','n',False), ('s','s',True)]
def pat(x, y): return ('s' if x == 9 else 'n', 's' if y == 9 else 'n', x == y)

def closure(I, N, Qs, vals):
    S = set(vals)
    while True:
        T = set(S)
        for a in S:
            T.add(N[a])
            for Q in Qs: T.add(Q[a])
            for b in S: T.add(I[a][b])
        if T == S: return sorted(S)
        S = T

def zf_ok(I, N, Qn, eqn, eln, D, S):
    M = (I, N, Qn, eqn, eln)
    for f in (EXT, POW, UNI, INF):
        if cev(f, M) not in D: return False
    return all(cev(REP(PH), M, a) in D for a in S)

def fails(I, N, Qn, Qs, EQ, EL, D):
    S = closure(I, N, (Qn, Qs), list(EQ.values()) + list(EL.values()))
    d = lambda v: v in D
    Q = lambda x: Qs if x == 9 else Qn
    eq = lambda x, y: EQ[pat(x, y)]
    el = lambda x, y: EL[pat(x, y)]
    bad = set()
    for a in S:
        for b in S:
            if d(a) and d(I[a][b]) and not d(b): bad.add('DET')
            if not d(I[a][I[N[a]][b]]): bad.add('B3')
        if not d(I[I[N[a]][a]][a]): bad.add('B2')
        for c in S:
            for b in S:
                if not d(I[I[a][b]][I[I[b][c]][I[a][c]]]): bad.add('B1'); break
    for Qx in (Qn, Qs):
        for a in S:
            if d(a) and not d(Qx[a]): bad.add('GEN')
            if not d(I[N[Qx[N[Qx[a]]]]][a]): bad.add('B6c')
            for b in S:
                if not d(I[Qx[I[a][b]]][I[Qx[a]][Qx[b]]]): bad.add('B4')
    for a in S:
        if not (d(I[Qn[Qs[a]]][Qs[Qn[a]]]) and d(I[Qs[Qn[a]]][Qn[Qs[a]]])): bad.add('B6b')
    for x in VARS:
        for y in VARS:
            if not d(N[Q(x)[N[eq(x, y)]]]): bad.add('B7')
            for z in VARS:
                if z != x and z != y:
                    e1, e2 = eq(x, y), el(x, y)
                    if not d(N[I[I[e1][Q(z)[e1]]][N[I[e2][Q(z)[e2]]]]]): bad.add('B6a')
                if not d(I[eq(x, y)][I[eq(x, z)][eq(y, z)]]): bad.add('B8a')
                if not d(I[eq(x, y)][I[el(x, z)][el(y, z)]]): bad.add('B8b')
                if not d(I[eq(x, y)][I[el(z, x)][el(z, y)]]): bad.add('B8c')
    if not zf_ok(I, N, Qn, EQ[PATS[0]], EL[PATS[0]], D, S): bad.add('ZF')
    return bad

def propmats(nv):
    vals = range(nv)
    Ds = [set(c) for r in range(1, nv) for c in itertools.combinations(vals, r)]
    for It in itertools.product(vals, repeat=nv*nv):
        I = [It[i*nv:(i+1)*nv] for i in vals]
        for N in itertools.product(vals, repeat=nv):
            for D in Ds:
                if any(a in D and I[a][b] in D and b not in D for a in vals for b in vals): continue
                if any(I[I[N[a]][a]][a] not in D for a in vals): continue
                if any(I[a][I[N[a]][b]] not in D for a in vals for b in vals): continue
                if any(I[I[a][b]][I[I[b][c]][I[a][c]]] not in D for a in vals for b in vals for c in vals): continue
                yield I, N, D

if __name__ == '__main__':
    nv = int(sys.argv[1]); targets = set(sys.argv[2].split(','))
    vals = range(nv); found = {}
    for I, N, D in propmats(nv):
        for Qn in itertools.product(vals, repeat=nv):
            for eqn in vals:
                for eln in vals:
                    S0 = closure(I, N, (Qn,), [eqn, eln])
                    if not zf_ok(I, N, Qn, eqn, eln, D, S0): continue
                    for Qs in itertools.product(vals, repeat=nv):
                        for rest in itertools.product(vals, repeat=8):
                            EQ = dict(zip(PATS, (eqn,) + rest[:4])); EL = dict(zip(PATS, (eln,) + rest[4:]))
                            bad = fails(I, N, Qn, Qs, EQ, EL, D)
                            if len(bad) == 1:
                                t = next(iter(bad))
                                if t in targets and t not in found:
                                    found[t] = (I, N, sorted(D), Qn, Qs, EQ, EL)
                                    print(t, found[t], flush=True)
                                    if set(found) >= targets: sys.exit(0)
    print('done; found', sorted(found), flush=True)
