"""Candidate NG' sentences (¬Goldbach) in the pure {∈,=} language, as role-named ASTs (ngdsl).

Common design: numbers are finite von Neumann ordinals n; arithmetic is cardinal arithmetic of
subsets of n (no pairs, no recursion).
  NG' = ∃n [ Nat(n) ∧ Ev(n) ∧ GF(n) ]
  Nat(n) : n is a finite ordinal (transitive, ∈-trichotomous, every nonempty X ⊆ n has an
           ∈-minimal and an ∈-maximal element)
  Ev(n)  : n has a 2-column grid with ≥ 2 rows          (n even, n ≥ 4)
  GF(n)  : for every split n = A ⊔ B, A or B is small (≤ 1) or composite
  Comp(X): X carries an R×C grid (R, C partitions of X, |r∩c| = 1, |R|, |C| ≥ 2)
Options `o` select conjunct orders and alternative sub-encodings (see OPTS).
"""
from ngdsl import *

class Fresh:
    def __init__(self): self.k = {}
    def __call__(self, base):
        self.k[base] = self.k.get(base, 0) + 1
        return f'{base}{self.k[base]}'

def A2(p, q, flip): return an(q, p) if flip else an(p, q)

def tr(fr, s):
    y, z = fr('ty'), fr('tz')
    return ball(y, s, ball(z, y, el(z, s)))

def trich(fr, n, o):
    x, y = fr('cx'), fr('cy')
    body = ors(el(x, y), eq(x, y), el(y, x)) if not o.get('trich2') else ors(el(x, y), el(y, x), eq(x, y))
    return ball(x, n, ball(y, n, body))

def minmax(fr, n, o):
    X, u, z = fr('mX'), fr('mu'), fr('mz')
    m1, k1, m2, k2 = fr('mm'), fr('mk'), fr('mm'), fr('mk')
    mn = bex(m1, X, ball(k1, X, no(el(k1, m1))))
    mx = bex(m2, X, ball(k2, X, no(el(m2, k2))))
    if o.get('mm_split'):     # two separate subset quantifiers
        X2, u2, z2 = fr('mX'), fr('mu'), fr('mz')
        a = al(X, im(sub(u, X, n), ball(z, X, mn)))
        b = al(X2, im(sub(u2, X2, n), ball(z2, X2, mx)))
        return A2(a, b, o.get('mmf', 0))
    return al(X, im(sub(u, X, n), ball(z, X, A2(mn, mx, o.get('mmf', 0)))))

def nat(fr, n, o):
    if o.get('htr'):                  # hereditarily transitive instead of trichotomy
        x = fr('hx')
        mid = ball(x, n, tr(fr, x))
    else:
        mid = trich(fr, n, o)
    parts = [tr(fr, n), mid, minmax(fr, n, o)]
    perm = list(itertools.permutations(range(3)))[o.get('natp', 0)]
    ps = [parts[i] for i in perm]
    return A2(ps[0], A2(ps[1], ps[2], False), False) if not o.get('natl') else A2(A2(ps[0], ps[1], False), ps[2], False)

def le2(fr, R):
    r, x, y, z = fr('lr'), fr('lx'), fr('ly'), fr('lz')
    return ball(r, R, ex(x, ex(y, ball(z, r, orr(eq(z, x), eq(z, y))))))

def half(fr, X, R, C, o):
    """the row half of a grid: R ⊆ P(X) partition of X, some row has 2 points, rows meet columns once"""
    r, x = fr('sr'), fr('sx'); subR = ball(r, R, ball(x, r, el(x, X)))
    x = fr('vx'); r = fr('vr'); cov = ball(x, X, bex(r, R, el(x, r)))
    r, s, x = fr('ur'), fr('us'), fr('ux'); uni = ball(r, R, ball(s, R, ball(x, r, im(el(x, s), eq(r, s)))))
    r, x, y = fr('nr'), fr('nx'), fr('ny'); nt = bex(r, R, bex(x, r, bex(y, r, el(x, y))))
    r, c, x, y = fr('gr'), fr('gc'), fr('gx'), fr('gy')
    g1 = ball(r, R, ball(c, C, bex(x, r, A2(el(x, c), ball(y, r, im(el(y, c), eq(y, x))), o.get('g1f', 0)))))
    parts = [subR, cov, uni, nt, g1]
    perm = o.get('hperm', (0, 1, 2, 3, 4))
    ps = [parts[i] for i in perm]
    return ands(*ps)

def comp(fr, X, n, o):
    """Comp*(X): X has an R×C grid with |R|,|C| ≥ 2, and (X = n → every row has ≤ 2 points)."""
    R, C = fr('R'), fr('C')
    if o.get('swap', 1):
        T = fr('T')
        h1 = half(fr, X, R, C, o)
        # second copy of the SAME text (same roles, rebound): (R, C) := (C, R) through T
        sw = ex(T, an(eq(T, R), ex(R, an(eq(R, C), ex(C, an(eq(C, T), h1))))))
        core = A2(h1, sw, o.get('swf', 0))
    else:
        core = an(half(fr, X, R, C, o), half(fr, X, C, R, o))
    guard = im(eq(X, n), le2(fr, R))
    return ex(R, ex(C, A2(core, guard, o.get('gf', 0))))

def small(fr, X):
    y, x = fr('ky'), fr('kx')
    return ex(y, ball(x, X, eq(x, y)))

def split(fr, n, A, B, o):
    x = fr('px')
    OR = orr(el(x, A), el(x, B))
    cov = im(el(x, n), OR)
    sub_ = im(OR, el(x, n))
    dis = im(el(x, A), no(el(x, B)))
    return al(x, A2(cov, A2(sub_, dis, o.get('spf2', 0)), o.get('spf', 0)))

def gf(fr, n, o, X, cp):
    A, B = fr('A'), fr('B')
    ch = orr(eq(X, A), eq(X, B))
    np_ = orr(small(fr, X), cp) if not o.get('npf') else orr(cp, small(fr, X))
    return al(A, al(B, im(split(fr, n, A, B, o), ex(X, A2(ch, np_, o.get('chf', 0))))))

def ev(fr, n, o, X, cp):
    return ex(X, A2(eq(X, n), cp, o.get('evf', 0)))

def ngA(o=None):
    o = o or {}
    fr = Fresh()
    n = fr('n')
    X = 'X'
    cp = comp(fr, X, n, o)          # one AST, used in Ev and in GF (identical text)
    parts = [nat(fr, n, o), ev(fr, n, o, X, cp), gf(fr, n, o, X, cp)]
    perm = list(itertools.permutations(range(3)))[o.get('topp', 0)]
    ps = [parts[i] for i in perm]
    body = A2(ps[0], A2(ps[1], ps[2], False), False) if not o.get('topl') else A2(A2(ps[0], ps[1], False), ps[2], False)
    return ex(n, body)

if __name__ == '__main__':
    import sys
    f = ngA()
    lab = greedy_labels(f)
    print(show(f))
    print(len(roles(f)), 'roles; labels used', sorted(set(lab.values())))
    for place in ['after', 'before', 'inV', 'inV2', 'inCG']:
        st, nt, _ = measure(f, lab, place)
        print(place, 'tokens', nt, 'states', st)
