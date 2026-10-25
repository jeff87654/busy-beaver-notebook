"""High-level evaluation of Kd-family runs with huge counters (residues mod 2^K).

Uses modexact (exact residue maps h_j of the clearing functions U_j) plus the STABLE-DEPTH fact, verified here for the
chosen K by a fixed-point check: for j >= JS, h_j = h_JS, X_j = X_JS (mod 2^K) and the orbit of X_JS under h_JS has
preperiod 0 and period 2.  By induction h_{j+1} is then the same map for every j >= JS, so for any depth j >= JS and any
counter x >= 2j:  U_j(x) = EK (mod 2^K) if x is even, OK_ (mod 2^K) if x is odd.  Every unit flips the parity of b
(U_0(x) = 3x+7; for j >= 1 this is the BB(9)-champion Coq lemma `parity`), hence a digit v >= 1 at a stable depth maps
b to EK if b+v is odd and to OK_ if b+v is even.
"""
import modexact as E
from modexact import Huge


class PrecisionError(Exception):
    pass


class Setup:
    def __init__(self, K=16):
        E.setK(K)
        self.K = K
        self.M = 1 << K
        prev = None
        js = None
        for j in range(0, 40):
            hj = E.hmap(j)
            if prev is not None and hj == prev:
                r, p, q = E.orbit(j - 1)
                if p == 0 and q == 2 and E.res(E.Xj(j)) == E.res(E.Xj(j - 1)):
                    js = j - 1
                    break
            prev = hj
        assert js is not None, 'no stable depth found'
        # fixed-point check: h_{js+1} == h_js and the orbit of X_js under h_js is (X, h(X)) with h(h(X)) = X
        r, p, q = E.orbit(js)
        assert p == 0 and q == 2
        self.JS = js
        self.EK = E.hmap(js)[0]       # U_j(even) residue
        self.OK = E.hmap(js)[1]       # U_j(odd) residue
        assert all(E.hmap(js)[x] == (self.EK if x % 2 == 0 else self.OK) for x in range(self.M))


def par(x):
    return (x.r if isinstance(x, Huge) else x) & 1


def mkres(r):
    return Huge(r % E.M)


def uiter_any(S, j, v, b, vbits=None):
    """U_j^v(b) where v may be Huge (known mod 2^vbits)."""
    if not isinstance(v, Huge):
        if not isinstance(b, Huge) and j >= 1:
            if not 2 * j <= b:
                raise ValueError('invariant 2j <= b fails at depth %d, b=%d' % (j, b))
        return E.Uiter(j, v, b)
    # huge iteration count
    if j >= S.JS:
        # parity rule; requires one unit at least (v huge)
        return Huge(S.EK if (par(b) + par(v)) % 2 == 1 else S.OK)
    # shallow depth: bring b to Huge first
    y = b
    i = 0
    while not isinstance(y, Huge):
        y = E.U(j, y)
        i += 1
    hj = E.hmap(j)
    seen = {}
    seq = []
    cur = y.r
    while cur not in seen:
        seen[cur] = len(seq)
        seq.append(cur)
        cur = hj[cur]
    p0 = seen[cur]
    q = len(seq) - p0
    kb = vbits if vbits is not None else S.K
    if (1 << kb) % q:
        raise PrecisionError('period %d at depth %d needs more bits than %d' % (q, j, kb))
    nrem = (v.r - i)          # v - i  (v huge)
    return Huge(seq[p0 + (nrem - p0) % q])


def clear_exact_list(S, ds, b, depth0=0, vbits=None):
    """clear an explicit digit list (ints or Huge) from counter b; digit i sits at depth depth0+i.
    Huge digits are known only mod 2^vbits (default: full precision)."""
    for i, v in enumerate(ds):
        if not isinstance(v, Huge) and v == 0:
            continue
        b = uiter_any(S, depth0 + i, v, b, vbits)
    return b


def lin_val(c, n, nbits):
    """value c1*n + c0 for an int n or a Huge n known mod 2^nbits (c1, c0 integer Fractions)"""
    c1, c0 = int(c[0]), int(c[1])
    if not isinstance(n, Huge):
        return c1 * n + c0
    if c1 == 0:
        return c0
    return Huge((c1 * n.r + c0) % (1 << nbits))


def clear_template(S, t, n, nbits, b):
    """clear the template list P + B^(alpha n + beta) + S for a HUGE n (known mod 2^nbits) from counter b.
    Returns (result, info) where info has the depth slope etc."""
    P = [lin_val(c, n, nbits) for c in t['P']]
    Bk = [lin_val(c, n, nbits) for c in t['B']]
    Sx = [lin_val(c, n, nbits) for c in t['S']]
    alpha, beta = t['alpha'], t['beta']
    if not any(isinstance(v, Huge) or v != 0 for v in P + Bk + Sx):
        raise PrecisionError('template without a nonzero digit')
    if alpha == 0:
        ds = P + Sx
        return clear_exact_list(S, ds, b, 0, nbits), {'deep': False}
    # explicit part: prefix and the first few blocks, until the depth is stable and b is huge
    depth = 0
    for v in P:
        if isinstance(v, Huge) or v != 0:
            b = uiter_any(S, depth, v, b, nbits)
        depth += 1
    k = 0
    blen = len(Bk)
    while k < 64 and (depth < S.JS or not isinstance(b, Huge)):
        for v in Bk:
            if isinstance(v, Huge) or v != 0:
                b = uiter_any(S, depth, v, b, nbits)
            depth += 1
        k += 1
    if not isinstance(b, Huge) or depth < S.JS:
        raise PrecisionError('template clearing did not reach a stable huge state')
    # remaining blocks: count c = alpha*n + beta - k (huge), then the suffix; all at stable depths
    if not any(isinstance(v, Huge) or v != 0 for v in Bk + Sx):
        return b, {'deep': True}
    cpar = (alpha * (n.r & 1) + beta - k) & 1
    units = cpar * sum(par(v) for v in Bk) + sum(par(v) for v in Sx)
    res = S.EK if (par(b) + units) % 2 == 1 else S.OK
    return Huge(res), {'deep': True}
