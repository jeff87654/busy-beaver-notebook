"""Semantic test: one main() iteration of a candidate .tm (symbolic RM, symrm.py) against an independent
reference implementation of the abstract enumerator (Python port of coq/Enum.v enum_step, generalized to a
clause list / per-clause parameter permutation / order).

usage: python semtest.py CAND.tm CAND.json [trials] [seed]
CAND.json: {"clauses": [...names...], "perm": {name: [i,j,k]}, "order": [...], "variant": {...}}

The reference formulas below are written from Logic.v / zf2.nql, NOT from the program tokens."""
import sys, json, random
from symrm import SymRM, cpair, cunpair, Big, isz, add

def weq(x, y): return cpair(cpair(x, y), 0)
def wel(x, y): return cpair(cpair(x, y), 1)
def wim(a, b): return cpair(cpair(a, b), 2)
def wn(a): return cpair(a, 3)
def wal(x, a): return cpair(cpair(x, a), 4)
def wex(x, a): return wn(wal(x, wn(a)))
def wa(a, b): return wn(wim(a, wn(b)))
def wo(a, b): return wim(wn(a), b)
def wbi(a, b): return wa(wim(a, b), wim(b, a))

def REP(ph, m=(0, 1, 2, 3)):
    v0, v1, v2, v3 = m
    E = wex(v3, wa(wel(v3, v0), wal(v1, ph)))
    return wim(wal(v3, wex(v1, wal(v2, wim(wal(v1, ph), weq(v2, v1))))),
               wex(v1, wal(v2, wa(wim(wel(v2, v1), E), wim(E, wel(v2, v1))))))
def EXT(m=(0, 1, 2, 3)):
    v0, v1, v2, v3 = m
    return wim(wal(v2, wa(wim(wel(v2, v0), wel(v2, v1)), wim(wel(v2, v1), wel(v2, v0)))), weq(v0, v1))
def POW(m=(0, 1, 2, 3)):
    v0, v1, v2, v3 = m
    return wex(v1, wal(v2, wim(wal(v3, wim(wel(v3, v2), wel(v3, v0))), wel(v2, v1))))
def UNI(m=(0, 1, 2, 3)):
    v0, v1, v2, v3 = m
    return wex(v1, wal(v2, wim(wex(v3, wa(wel(v2, v3), wel(v3, v0))), wel(v2, v1))))
def INF(m=(0, 1, 2, 3)):
    v0, v1, v2, v3 = m
    return wex(v1, wa(wel(v0, v1), wal(v0, wim(wel(v0, v1), wex(v2, wa(wel(v2, v1),
               wal(v1, wa(wim(wel(v1, v2), weq(v1, v0)), wim(weq(v1, v0), wel(v1, v2))))))))))

# closed / schematic clause formulas in roles a, b, c (role values = the permuted parameters)
FORM = {
    'B1':  lambda a, b, c: wim(wim(a, b), wim(wim(b, c), wim(a, c))),
    'B2':  lambda a, b, c: wim(wim(wn(a), a), a),
    'B3':  lambda a, b, c: wim(a, wim(wn(a), b)),
    'B4':  lambda a, b, c: wim(wal(a, wim(b, c)), wim(wal(a, b), wal(a, c))),
    'B6b': lambda a, b, c: wim(wal(a, wal(b, c)), wal(b, wal(a, c))),
    'B6c': lambda a, b, c: wim(wex(a, wal(a, b)), b),
    'B7':  lambda a, b, c: wex(a, weq(a, b)),
    'B8a': lambda a, b, c: wim(weq(a, b), wim(weq(a, c), weq(b, c))),
    'B8b': lambda a, b, c: wim(weq(a, b), wim(wel(a, c), wel(b, c))),
    'B8c': lambda a, b, c: wim(weq(a, b), wim(wel(c, a), wel(c, b))),
    'B8bc': lambda a, b, c: wim(weq(a, b), wa(wim(wel(a, c), wel(b, c)), wim(wel(c, a), wel(c, b)))),
    'B8abc': lambda a, b, c: wim(weq(a, b), wa(wim(weq(a, c), weq(b, c)),
                                              wa(wim(wel(a, c), wel(b, c)), wim(wel(c, a), wel(c, b))))),
    'B6a': lambda a, b, c: (0 if c == a or c == b else
                            wa(wim(weq(a, b), wal(c, weq(a, b))), wim(wel(a, b), wal(c, wel(a, b))))),
    'EXT': lambda a, b, c: EXT(),
    'REP': lambda a, b, c: REP(a),
    'POW': lambda a, b, c: POW(),
    'UNI': lambda a, b, c: UNI(),
    'INF': lambda a, b, c: INF(),
}
EXTRA = {}   # variant formulas registered by candidate configs (see variants in RESULTS.md)

VMAP = {}
FLIPS = {}
DETSWAP = False

def tree_code(t, ph):
    k = t[0]
    if k == 'ph': return ph
    if k == 'eq': return weq(t[1], t[2])
    if k == 'el': return wel(t[1], t[2])
    if k == 'n': return wn(tree_code(t[1], ph))
    if k == 'al': return wal(t[1], tree_code(t[2], ph))
    if k == 'ex': return wex(t[1], tree_code(t[2], ph))
    if k == 'im': return wim(tree_code(t[1], ph), tree_code(t[2], ph))
    if k == 'a': return wa(tree_code(t[1], ph), tree_code(t[2], ph))
    raise ValueError(t)

def apply_clause(name, p, perm, ws):
    """effect of the selected clause on (topwff, wffstack); p = (p1, p2, p3) from the proof list."""
    a, b, c = (p[i - 1] for i in perm)
    if name == 'DET':          # roles: a = ps, b <- major (2nd pop), c <- minor (1st pop)
        ph, ws1 = cunpair(ws)
        maj, ws2 = cunpair(ws1)
        if DETSWAP: ph, maj = maj, ph       # variant: major premise popped first
        return (a if wim(ph, a) == maj else 0), ws2
    if name == 'GEN':          # roles: a = variable, c <- premise
        ph, ws1 = cunpair(ws)
        return wal(a, ph), ws1
    base = name.split('#')[0]
    f = EXTRA.get(name) or FORM.get(base)
    if base == 'PU':      # E. v1 A. v2 ( ( POWmatrix \/ UNImatrix ) -> v2 e. v1 ), written out by hand
        m = tuple(VMAP.get(name, (0, 1, 2, 3)))
        if name not in FLIPS and m == (0, 1, 2, 3):
            P = wal(3, wim(wel(3, 2), wel(3, 0))); U = wex(3, wa(wel(2, 3), wel(3, 0)))
            return wex(1, wal(2, wim(wim(wn(P), U), wel(2, 1)))), ws
    if base == 'INF2' and name not in FLIPS and name not in VMAP:   # written out by hand
        return wex(1, wa(wel(0, 1), wal(0, wim(wel(0, 1), wex(2, wa(wel(2, 1),
                   wa(wal(1, wim(wel(1, 2), weq(1, 0))), wel(0, 2)))))))), ws
    if base in ('EXT', 'REP', 'POW', 'UNI', 'INF', 'PU', 'INF2'):
        if name in FLIPS or name in VMAP or base in ('PU', 'INF2'):
            import forms
            t = forms.variant(forms.TREES[base], tuple(VMAP.get(name, (0, 1, 2, 3))), FLIPS.get(name, 0))
            return tree_code(t, a), ws
        return f(a, b, c), ws
    return f(a, b, c), ws

def enum_step(st, clauses, perm, order):
    pl, np, tw, ws = st
    if isz(pl): pl1, np1 = np, add(np, 1)
    else: pl1, np1 = (pl - 1 if isinstance(pl, int) else Big(pl.t, pl.off - 1)), np
    ac, r = cunpair(pl1); p1, r = cunpair(r); p2, r = cunpair(r); p3, pl5 = cunpair(r)
    ws1 = cpair(tw, ws)
    if isz(ac): tw2, ws2 = 0, ws1
    else:
        k = min(ac, len(order)) - 1 if isinstance(ac, int) else len(order) - 1
        name = clauses[order[k]]
        tw2, ws2 = apply_clause(name, (p1, p2, p3), tuple(perm.get(name, (1, 2, 3))), ws1)
    return (pl5, np1, tw2, ws2)

def rand_wff(rng, depth=0):
    r = rng.random()
    if depth > 3 or r < 0.3: return rng.randrange(0, 6)
    k = rng.randrange(5)
    if k == 0: return weq(rng.randrange(4), rng.randrange(4))
    if k == 1: return wel(rng.randrange(4), rng.randrange(4))
    if k == 2: return wim(rand_wff(rng, depth + 1), rand_wff(rng, depth + 1))
    if k == 3: return wn(rand_wff(rng, depth + 1))
    return wal(rng.randrange(4), rand_wff(rng, depth + 1))

def run(tmpath, cfg, trials=1500, seed=7, verbose=True):
    clauses, order = cfg['clauses'], cfg['order']
    perm = {k: tuple(v) for k, v in cfg.get('perm', {}).items()}
    VMAP.clear(); VMAP.update({k: tuple(v) for k, v in cfg.get('vmap', {}).items()})
    FLIPS.clear(); FLIPS.update(cfg.get('flips', {}))
    global DETSWAP; DETSWAP = 'detswap' in cfg.get('opt', [])
    S = SymRM(tmpath)
    R_of = lambda st: None
    idx = S.regidx
    rng = random.Random(seed)
    N = len(order); bad = 0; sel = {}
    for t in range(trials):
        # choose a proof step: axiom code, params (small, often colliding, sometimes wffs), rest
        ac = rng.choice(list(range(0, N + 3)) + list(range(1, N + 1)) * 3)
        pv = lambda: rng.choice([rng.randrange(0, 3), rng.randrange(0, 3), rng.randrange(0, 3), rand_wff(rng)])
        p1, p2, p3 = pv(), pv(), pv()
        rest = rng.choice([0, 0, rng.randrange(1, 50)])
        tw = rand_wff(rng); ws = cpair(rand_wff(rng), cpair(rand_wff(rng), rng.choice([0, rand_wff(rng)])))
        k = min(ac, N) - 1
        if ac and clauses[order[k]] == 'DET' and rng.random() < 0.6:
            # make the major premise match: maj = (tw -> ps) where ps = the 'a' role parameter
            a_reg = perm.get('DET', (1, 2, 3))[0]
            if rng.random() < 0.3:      # ps = 1 = code of v0 e. v0: the machine must halt
                if a_reg == 1: p1 = 1
                elif a_reg == 2: p2 = 1
                else: p3 = 1
            ps = (p1, p2, p3)[a_reg - 1]
            ws = cpair(wim(tw, ps), cpair(rand_wff(rng), 0))
            if DETSWAP:       # major on top: tw (pushed by main) is the major, next is the minor
                mn = rand_wff(rng); tw = wim(mn, ps); ws = cpair(mn, cpair(rand_wff(rng), 0))
        pl1 = cpair(ac, cpair(p1, cpair(p2, cpair(p3, rest))))
        if rng.random() < 0.15:
            pl, np = 0, pl1          # exercise the nextproof branch
        else:
            pl = pl1 + 1 if isinstance(pl1, int) else Big(pl1.t, 1); np = rng.randrange(0, 1000)
        st = (pl, np, tw, ws)
        exp = enum_step(st, clauses, perm, order)
        R = [0] * S.nreg
        R[idx['prooflist']], R[idx['nextproof']], R[idx['topwff']], R[idx['wffstack']] = st
        # junk in axiomcode / params (main() must zero them)
        junk = ('axiomcode',) if 'b6aD' in cfg.get('opt', []) else ('axiomcode', 'param1', 'param2', 'param3')
        for r in junk:
            R[idx[r]] = rng.randrange(0, 5)
        try:
            halted = S.main(R)
        except Exception as ex:
            bad += 1
            if verbose: print('EXCEPTION', type(ex).__name__, ex, 'ac', ac, 'clause', clauses[order[k]] if ac else '-')
            continue
        got = (R[idx['prooflist']], R[idx['nextproof']], R[idx['topwff']], R[idx['wffstack']])
        scratch_ok = all(isz(R[idx[r]]) for r in idx if r.startswith('scratch'))
        if 'b6aD' in cfg.get('opt', []):   # invariant: params are 0 at the start of main()
            scratch_ok = scratch_ok and all(isz(R[idx[r]]) for r in ('param1', 'param2', 'param3'))
        expect_halt = exp[2] == 1
        nm = clauses[order[k]] if ac else '-'
        sel[nm] = sel.get(nm, 0) + 1
        if expect_halt: sel['(halts)'] = sel.get('(halts)', 0) + 1
        if halted != expect_halt or (not halted and (got != exp or not scratch_ok)):
            bad += 1
            if verbose and bad <= 5:
                print('MISMATCH clause', nm, 'ac', ac, 'p', (p1, p2, p3), '\n  exp', exp, '\n  got', got, R)
    if verbose:
        print('semtest', tmpath, 'trials', trials, 'mismatches', bad)
        print('  selected:', dict(sorted(sel.items())))
    return bad

if __name__ == '__main__':
    cfg = json.load(open(sys.argv[2]))
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    sys.exit(1 if run(sys.argv[1], cfg, trials, seed) else 0)

def check_trees():
    """the default (unrenamed, unflipped) trees of forms.py must code exactly the Logic.v formulas above"""
    import forms
    ph = wim(weq(0, 1), wel(2, 3))
    ok = all(tree_code(forms.variant(forms.TREES[n]), ph) == v for n, v in
             [('EXT', EXT()), ('REP', REP(ph)), ('POW', POW()), ('UNI', UNI()), ('INF', INF())])
    print('forms.py trees match the reference formulas:', ok)
    return ok
