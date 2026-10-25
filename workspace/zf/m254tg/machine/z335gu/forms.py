"""Closed ZF axioms as formula trees, with trivially-equivalent variants (Track B).

A variant is given by (vmap, flips):
  vmap  : variable renaming v_i -> v_vmap[i] (injective into 0..4; v_4 costs nothing extra since wal uses it)
  flips : bitmask over the 'a' (conjunction), 'bi' (biconditional) and 'eq' nodes in tree order; a set
          bit swaps the operands (A /\\ B -> B /\\ A, A <-> B -> B <-> A, x = y -> y = x).
Every variant is equivalent to the original axiom over pure logic (alphabetic variance, commutativity
of /\\ and <->, symmetry of =).

Trees: ('eq',x,y) ('el',x,y) ('im',A,B) ('n',A) ('al',x,A) ('ex',x,A) ('a',A,B) ('bi',A,B) ('ph',) = REP's
schematic wff parameter (role a)."""

def EQ(x, y): return ('eq', x, y)
def EL(x, y): return ('el', x, y)
def IM(a, b): return ('im', a, b)
def N(a): return ('n', a)
def AL(x, a): return ('al', x, a)
def EX(x, a): return ('ex', x, a)
def A(a, b): return ('a', a, b)
def BI(a, b): return ('bi', a, b)
PH = ('ph',)

# exactly the formulas of coq/Logic.v (biconditional written as BI = (A -> B) /\ (B -> A))
TREES = {
    'EXT': IM(AL(2, BI(EL(2, 0), EL(2, 1))), EQ(0, 1)),
    'REP': IM(AL(3, EX(1, AL(2, IM(AL(1, PH), EQ(2, 1))))),
              EX(1, AL(2, BI(EL(2, 1), EX(3, A(EL(3, 0), AL(1, PH))))))),
    'POW': EX(1, AL(2, IM(AL(3, IM(EL(3, 2), EL(3, 0))), EL(2, 1)))),
    'UNI': EX(1, AL(2, IM(EX(3, A(EL(2, 3), EL(3, 0))), EL(2, 1)))),
    'INF': EX(1, A(EL(0, 1), AL(0, IM(EL(0, 1), EX(2, A(EL(2, 1), AL(1, BI(EL(1, 2), EQ(1, 0))))))))),
}
# Track B (set-theoretic equivalence): one axiom giving a set containing all subsets and all elements of
# elements of v0:  E. v1 A. v2 ( ( A. v3 ( v3 e. v2 -> v3 e. v0 ) \/ E. v3 ( v2 e. v3 /\ v3 e. v0 ) ) -> v2 e. v1 )
# with  A \/ B  :=  -. A -> B.  Equivalent to POW /\ UNI given separation (REP) and pairing.
# Track B (pure-logic equivalent): z = {x} written as  A. w ( w e. z -> w = x ) /\ x e. z  instead of
# A. w ( w e. z <-> w = x )   (equivalent in FOL with equality: <= by B8b substitution).
TREES['INF2'] = EX(1, A(EL(0, 1), AL(0, IM(EL(0, 1), EX(2, A(EL(2, 1), A(AL(1, IM(EL(1, 2), EQ(1, 0))), EL(0, 2))))))))
TREES['PU'] = EX(1, AL(2, IM(IM(N(AL(3, IM(EL(3, 2), EL(3, 0)))), EX(3, A(EL(2, 3), EL(3, 0)))), EL(2, 1))))

# ---- zf-axtext candidates ----
def SUB(z, y, v): return AL(v, IM(EL(v, z), EL(v, y)))      # z C_ y  (bound variable v)
def OR(a, b): return IM(N(a), b)
_RCONC = EX(1, AL(2, BI(EL(2, 1), EX(3, A(EL(3, 0), AL(1, PH))))))
def _rep(c): return IM(AL(3, EX(1, AL(2, IM(AL(1, PH), c)))), _RCONC)
# REPb: fibers bounded by a set (z e. y) instead of "at most one z (z = y)"; UNI becomes derivable
TREES['REPb'] = _rep(EL(2, 1))
# REPs: fibers bounded by a power set (z C_ y); POW becomes derivable
for _v in (0, 3, 4):
    TREES['REPs%d' % _v] = _rep(SUB(2, 1, _v))
    # REPbs: z e. y \/ z C_ y; POW and UNI both derivable
    TREES['REPbs%d' % _v] = _rep(OR(EL(2, 1), SUB(2, 1, _v)))
    TREES['REPsb%d' % _v] = _rep(OR(SUB(2, 1, _v), EL(2, 1)))
# EXTs: EXT with the biconditional split (one more token; lets SUB subsequences be shared)
TREES['EXTs'] = IM(SUB(0, 1, 2), IM(SUB(1, 0, 2), EQ(0, 1)))
# REPq: the fiber bound z e. y \/ z C_ y with the disjunction pushed under the subset quantifier
for _v in (0, 3, 4):
    TREES['REPq%d' % _v] = _rep(AL(_v, IM(N(EL(2, 1)), IM(EL(_v, 2), EL(_v, 1)))))
    TREES['REPr%d' % _v] = _rep(AL(_v, IM(EL(_v, 2), IM(N(EL(2, 1)), EL(_v, 1)))))
REPLIKE = {'REP'} | {k for k in TREES if k.startswith('REP')}

def nflip(t):
    """number of flippable nodes"""
    k = t[0]
    if k in ('eq', 'el', 'ph'): return 1 if k == 'eq' else 0
    if k in ('n',): return nflip(t[1])
    if k in ('al', 'ex'): return nflip(t[2])
    return (1 if k in ('a', 'bi') else 0) + nflip(t[1]) + nflip(t[2])

def variant(t, vmap=(0, 1, 2, 3), flips=0):
    """apply renaming and flips; returns a tree without 'bi' (expanded) and with flips resolved"""
    vmap = tuple(vmap) + tuple(range(len(vmap), 5))
    ctr = [0]
    def bit():
        b = (flips >> ctr[0]) & 1; ctr[0] += 1; return b
    def go(t):
        k = t[0]
        if k == 'ph': return t
        if k == 'eq':
            x, y = vmap[t[1]], vmap[t[2]]
            return ('eq', y, x) if bit() else ('eq', x, y)
        if k == 'el': return ('el', vmap[t[1]], vmap[t[2]])
        if k == 'n': return ('n', go(t[1]))
        if k in ('al', 'ex'): return (k, vmap[t[1]], go(t[2]))
        if k == 'im': return ('im', go(t[1]), go(t[2]))
        if k == 'a':
            f = bit(); a, b = go(t[1]), go(t[2])
            return ('a', b, a) if f else ('a', a, b)
        if k == 'bi':
            f = bit(); a, b = go(t[1]), go(t[2])
            l, r = ('im', a, b), ('im', b, a)
            return ('a', r, l) if f else ('a', l, r)
        raise ValueError(t)
    return go(t)

def postfix(t):
    """program tokens (zfp SPEC syntax) building tree t; 'a' = REP's parameter role"""
    k = t[0]
    if k == 'ph': return ['a']
    if k == 'eq': return ['v%d' % t[1], 'v%d' % t[2], 'weq']
    if k == 'el': return ['v%d' % t[1], 'v%d' % t[2], 'wel']
    if k == 'n': return postfix(t[1]) + ['wn']
    if k == 'al': return ['v%d' % t[1]] + postfix(t[2]) + ['wal']
    if k == 'ex': return ['v%d' % t[1]] + postfix(t[2]) + ['wex']
    if k == 'im': return postfix(t[1]) + postfix(t[2]) + ['wim']
    if k == 'a': return postfix(t[1]) + postfix(t[2]) + ['wa']
    raise ValueError(t)

def show(t):
    k = t[0]
    if k == 'ph': return 'ph'
    if k == 'eq': return f'v{t[1]} = v{t[2]}'
    if k == 'el': return f'v{t[1]} e. v{t[2]}'
    if k == 'n': return '-. ' + show(t[1])
    if k == 'al': return f'A. v{t[1]} {show(t[2])}'
    if k == 'ex': return f'E. v{t[1]} {show(t[2])}'
    if k == 'im': return f'( {show(t[1])} -> {show(t[2])} )'
    if k == 'a': return f'( {show(t[1])} /\\ {show(t[2])} )'
    if k == 'bi': return f'( {show(t[1])} <-> {show(t[2])} )'
    raise ValueError(t)

if __name__ == '__main__':
    import zfp
    for nm, t in TREES.items():
        pf = ' '.join(postfix(variant(t)))
        print(nm, 'flips', nflip(t), 'matches zfp SPEC:', pf == zfp.SPEC[nm])
