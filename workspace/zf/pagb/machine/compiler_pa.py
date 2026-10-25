"""Completeness macros for the PA machine (zfc_254 macros with the slot count of this design) and their
contracts, checked through spec_pa.enum_step from random retained states.

Commands:  MP(x) = (0, x)   DROP = (1, 0)   NIP = (2, 0)   AX(c; x, y, u) = (3 + c, x, y, u)
Block contract  Build_X : (T, S, 0, 0) ->* (X, S, 0, 0) for all T, S (or an earlier halt, only at a
NIP whose cache is 1 = a derived F).

Derivations:  ('row', k, a, b, c, u)  root k of AX (k = 0: GEN slot ∀a h with h = 0 here is not
used; k >= 1: design.ROWS[k-1]) | ('bundle', a, b, c) | ('gen', i, D) | ('mp', DA, DAB, B).
"""
import random, sys
import spec_pa as spec
from spec_pa import P, wim, wal
import design

NS = spec.NSLOTS                 # slots pushed by AX: old current, GEN, rows
NR = len(design.ROWS)
MP = lambda x: (0, x)
DROP = (1, 0)
NIP = (2, 0)
def AX(c, x, y, u): return (3 + c, x, y, u)

def conclusion(D):
    k = D[0]
    if k == 'row':
        _, j, a, b, c, u = D
        return spec.ax_rows(a, 0, b, c, u)[1 + (j - 1)] if j >= 1 else wal(a, 0)
    if k == 'bundle':
        _, a, b, c = D[:4]; u = D[4] if len(D) > 4 else 0
        return spec.gated_bundle(a, b, c, u)
    if k == 'gen':
        return wal(D[1], conclusion(D[2]))
    if k == 'mp':
        A = conclusion(D[1]); I = conclusion(D[2])
        assert I == wim(A, D[3]), 'mp: major premise is not A -> B'
        return D[3]
    raise ValueError(D)

# DISCARD must leave current = 0, i.e. its AX must close the gate.  Old gate (c ∉ {a,b}): c = a = 1.
# Occurs-check gate (option a): b = Var(1) = 7 (h = 0 after the failed MP), so c = 1 ∈ vars T(b).
DISCARD = ([MP(1), AX(1, 0, 7, 0)] if getattr(design, 'GATE', 'ab') == 'occ' else [MP(1), AX(1, 0, 0, 0)]) + [NIP] * NS

def build(D):
    k = D[0]
    if k == 'row':
        _, j, a, b, c, u = D
        depth = NR + 1 - j                                    # 1 = top of stack (last row)
        return DISCARD + [AX(c, a, b, u)] + [NIP] * depth + [DROP] + [NIP] * (NS + 1 - depth)
    if k == 'bundle':
        _, a, b, c = D[:4]; u = D[4] if len(D) > 4 else 0
        return DISCARD + [AX(c, a, b, u)] + [NIP] * NS
    if k == 'gen':
        i = D[1]
        return build(D[2]) + [DROP, NIP, AX(i, i, 0, 0)] + [NIP] * (NS - 1) + [DROP, NIP, NIP]
    if k == 'mp':
        B = D[3]
        return (build(D[1]) + [DROP] + build(D[2]) + [NIP, DROP, NIP, MP(B), AX(B, 0, 0, 0)]
                + [NIP] * NS + [DROP, NIP, NIP])
    raise ValueError(D)

START = [AX(0, 1, 1, 0)]                                     # arbitrary (t,S,d,h) -> (R, S', 0, 0)
HALT_SUFFIX = [DROP, NIP, NIP]                               # (F,S,0,0) -> halt

def encode(cmds):
    e = 0
    for c in reversed(cmds):
        v = e
        for f in reversed(c[1:]):
            v = P(f, v)
        e = spec.add(P(c[0], v), 1)
    return e - 1

def run_cmds(state, cmds):
    t, S, d, h = state
    N = encode(cmds)
    s = (0, N, t, S, d, h)
    for i in range(len(cmds)):
        s2 = spec.enum_step(s)
        if s2 is None:
            return ('halt', i)
        s = s2
    assert s[0] == 0, 'candidate did not end where expected'
    return s[2:]

def rand_state(rnd, small_cache=None):
    if small_cache is None: small_cache = getattr(design, 'GATE', 'ab') == 'occ'
    def code():
        k = rnd.random()
        if k < 0.3: return rnd.randint(0, 3)
        if k < 0.6: return rnd.randint(0, 10**6)
        return rnd.choice([spec.wim, spec.wel, spec.wal, spec.weq])(rnd.randint(0, 9), rnd.randint(0, 10**9))
    S = rnd.choice([0, P(code(), 0), P(code(), P(code(), rnd.randint(0, 99)))])
    # occurs-check gate: START's AX walks T(h+1), linear in the value; keep the simulated cache small
    h = rnd.randint(0, 3000) if small_cache else code()
    return (code(), S, rnd.randint(0, 50), h)

def demo_derivations(rnd):
    a, b, c, u = (rnd.randint(0, 6) for _ in range(4))
    while c in (a, b):
        c += 1
    ds = [('bundle', a, b, c), ('bundle', a, a, c if c != a else a + 1), ('bundle', c + 1, b, c),
          ('bundle', 0, b if b else 1, c if c not in (0, b) else max(b, 1) + 1)]
    ds += [('row', j, a, b, c, u) for j in range(1, NR + 1)]
    ds += [('row', j, rnd.randint(0, 9), rnd.randint(0, 9), rnd.randint(0, 9), rnd.randint(0, 9))
           for j in range(1, NR + 1)]
    # GEN of a leaf and an MP node: GEN_x(Euclid) then QI, MP
    jE = design.ROWS.index(search_pa_EUC()) + 1
    jQ = design.ROWS.index(search_pa_QI()) + 1
    rE = ('row', jE, a, b, c, u)
    x = rnd.randint(0, 9)
    g = ('gen', x, rE)
    R = conclusion(rE)
    lhs, rhs = spec.unP(R // 4)
    qi = ('row', jQ, x, lhs, rhs, 0)
    B = wim(wal(x, lhs), wal(x, rhs))
    assert conclusion(qi) == wim(conclusion(g), B)
    m = ('mp', g, qi, B)
    ds += [g, m, ('gen', rnd.randint(0, 3), m)]
    return ds

def search_pa_EUC():
    return getattr(design.SR, 'EUC', None) or __import__('pavars').EUC
def search_pa_QI():
    import pavars; return pavars.QI

def main(n=100, seed=7):
    rnd = random.Random(seed)
    bad = 0; tested = 0
    for _ in range(n):
        for D in demo_derivations(rnd):
            X = conclusion(D)
            st = rand_state(rnd)
            st = (st[0], st[1], 0, 0)
            out = run_cmds(st, build(D))
            tested += 1
            if out[0] == 'halt':
                if st[0] != 1 and X != 1:
                    bad += 1; print('unexpected halt', D[:2], out)
                continue
            if not (out[0] == X and out[1] == st[1] and out[2] == 0 and out[3] == 0):
                bad += 1
                if bad < 5: print('CONTRACT FAIL', D[:2], st, out)
        st = rand_state(rnd)
        D = rnd.choice(demo_derivations(rnd))
        out = run_cmds(st, START + build(D))
        tested += 1
        if out[0] == 'halt':
            if conclusion(D) != 1:
                bad += 1; print('unexpected halt from arbitrary state', D[:2], out)
        elif not (out[0] == conclusion(D) and out[2] == 0 and out[3] == 0):
            bad += 1; print('START+Build fail', D[:2], st, out)
    for _ in range(50):
        st = rand_state(rnd); S = st[1]
        out = run_cmds((1, S, 0, 0), HALT_SUFFIX)
        if out != ('halt', 2):
            bad += 1; print('suffix fail', out)
    print('block contracts tested', tested, 'failures', bad)
    return bad

if __name__ == '__main__':
    raise SystemExit(1 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 100) else 0)
