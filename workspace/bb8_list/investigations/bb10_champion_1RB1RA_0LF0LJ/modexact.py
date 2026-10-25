"""Exact residues of the clearing functions U_j modulo M = 2^K, without the stabilisation heuristic of modeval.py.

Clearing functions (BB(9)-champion rules R1-R3, proved in Coq for that machine; the BB(10) champion runs the same
transitions):  U_0(x) = 3x+7;  U_{j+1}(x) = U_j^(x-2j)(X_j) for x >= 2j+2;  X_0 = 7, X_{j+1} = U_j(U_j(X_j)).
A digit v at depth j maps the counter b to U_j^v(b).

Numbers are Python ints while < LIMIT, otherwise Huge(residue mod M).  Every Huge value is >= LIMIT = 2^64 (all values
come from increasing maps, U_j(x) >= x + 2j + 5), which exceeds every threshold T_j below (asserted).
Residue maps: for x >= T_j, U_j(x) = h_j[x mod M] (mod M).  h_{j+1} is built from the orbit r_i = U_j^i(X_j) mod M:
preperiod p, period q; q must divide M (asserted), then U_{j+1}(x) = r_{p + (x-2j-p) mod q} for x-2j >= p, T_{j+1} = 2j+max(p,2).
"""
import sys

LIMIT = 1 << 64


class Huge:
    __slots__ = ('r',)

    def __init__(self, r):
        self.r = r

    def __repr__(self):
        return 'Huge(%d mod 2^%d)' % (self.r, K)


K = 16
M = 1 << K
h = {}      # j -> list of residues (length M)
T = {}      # j -> threshold
X = {}      # j -> X_j (int or Huge)


def setK(k):
    global K, M
    K = k
    M = 1 << k
    h.clear(); T.clear(); X.clear(); _orb.clear()


def res(x):
    return x.r if isinstance(x, Huge) else x % M


def mk(v):
    return v if v < LIMIT else Huge(v % M)


def U(j, x):
    """U_j(x) for an int or Huge x (requires x >= 2j for j >= 1)."""
    if isinstance(x, Huge):
        hj = hmap(j)
        assert T[j] < LIMIT
        return Huge(hj[x.r])
    if j == 0:
        return mk(3 * x + 7)
    assert x >= 2 * (j - 1) + 2, ('site condition 2j <= b fails', j, x)
    n = x - 2 * (j - 1)
    if j == 1:
        # U_1(x) = U_0^x(7) = (21*3^x - 7)/2
        if x <= 36:
            return mk((21 * 3 ** x - 7) // 2)
        return Huge(((21 * pow(3, x, 2 * M) - 7) % (2 * M)) // 2)
    return Uiter(j - 1, n, Xj(j - 1))


def Uiter(j, n, s):
    """U_j^n(s) for an exact iteration count n."""
    if n <= 64 or not isinstance(s, Huge):
        y = s
        i = 0
        while i < n:
            if isinstance(y, Huge):
                return Huge(hiter(j, n - i, y.r))
            y = U(j, y)
            i += 1
        return y
    return Huge(hiter(j, n, s.r))


_orb = {}


def orbit(j):
    """Residue orbit of U_j^i(X_j): returns (list r, preperiod p, period q); also T_{j+1}."""
    if j in _orb:
        return _orb[j]
    s = Xj(j)
    r = []
    seen = {}
    i = 0
    # exact prefix while small
    while not isinstance(s, Huge) and s < LIMIT and i < 10 ** 6:
        if j >= 1 and s < T_needed(j):
            pass
        rr = s % M
        r.append(rr)
        s = U(j, s)
        i += 1
        if isinstance(s, Huge):
            break
    # from here on use h_j (s is Huge >= LIMIT >= T_j)
    hj = hmap(j)
    cur = s.r if isinstance(s, Huge) else s % M
    start_h = len(r)
    while True:
        if cur in seen:
            p = seen[cur]
            q = len(r) - p
            break
        seen[cur] = len(r)
        r.append(cur)
        cur = hj[cur]
    # the exact prefix may contain values equal mod M to later ones: periodicity is only claimed from p on, and
    # seen[] only indexes the h-driven part, so p >= start_h.
    assert M % q == 0, ('period does not divide M', j, q)
    _orb[j] = (r, p, q)
    return _orb[j]


def T_needed(j):
    return 0


def hmap(j):
    if j in h:
        return h[j]
    if j == 0:
        h[0] = [(3 * x + 7) % M for x in range(M)]
        T[0] = 0
        return h[0]
    r, p, q = orbit(j - 1)
    base = 2 * (j - 1)
    T[j] = base + max(p, 2)
    h[j] = [r[p + ((x - base - p) % q)] for x in range(M)]
    return h[j]


def hiter(j, n, r0):
    """residue of U_j^n(y) for a Huge y with residue r0 (all iterates Huge)."""
    hj = hmap(j)
    # orbit of r0 under hj: find preperiod/period then index
    seen = {}
    seq = []
    cur = r0
    while cur not in seen:
        seen[cur] = len(seq)
        seq.append(cur)
        if len(seq) > n:
            return seq[n]
        cur = hj[cur]
    p = seen[cur]
    q = len(seq) - p
    if n < len(seq):
        return seq[n]
    return seq[p + (n - p) % q]


def Xj(j):
    if j in X:
        return X[j]
    if j == 0:
        X[0] = 7
    else:
        X[j] = U(j - 1, U(j - 1, Xj(j - 1)))
    return X[j]


def hiterH(j, n, y):
    """U_j^n(y) for Huge n (given as a Huge residue; requires the orbit period to divide M) and Huge y."""
    hj = hmap(j)
    seen = {}
    seq = []
    cur = y.r
    while cur not in seen:
        seen[cur] = len(seq)
        seq.append(cur)
        cur = hj[cur]
    p = seen[cur]
    q = len(seq) - p
    assert M % q == 0 and p <= 64, ('hiterH', p, q)
    return Huge(seq[p + (n.r - p) % q])


def clear(ds, b):
    """clear digits ds (top first) from counter b; returns the final b (int or Huge)."""
    for depth, v in enumerate(ds):
        if v == 0:
            continue
        if not isinstance(b, Huge):
            assert depth == 0 or 2 * depth <= b, ('invariant 2j <= b fails', depth, b)
        b = Uiter(depth, v, b)
    return b


def L10(b):
    m, r = divmod(b, 4)
    assert r in (0, 2)
    return [1 if r == 0 else 3] + [0, 0, 3] * m + [0, 0, 2]


if __name__ == '__main__':
    for k in (8, 12, 16, 20):
        setK(k)
        b1 = clear(L10(28), 0)
        print('K=%d: b1 = %r ; b1 mod 2^i for i=1..10: %s' % (k, b1, [res(b1) % (1 << i) for i in range(1, min(k, 10) + 1)]))
        print('   thresholds T_j:', [T[j] for j in sorted(T)][:30])
