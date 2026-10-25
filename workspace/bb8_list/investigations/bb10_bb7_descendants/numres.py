"""Exact-or-huge numbers for the abstract champion process.

A Num is either exact (a Python int, kept while it is small) or HUGE: only its residue modulo a divisor `mod` of
QBIG is known, and it is known to be astronomically large (larger than any representative we will ever use).
QBIG is lambda-closed (Carmichael lambda(QBIG) divides QBIG), so 2^x mod QBIG is computable from x mod QBIG
when x is huge (x >= 64 covers the 2-adic part).
"""
from math import gcd

PRIMES = {2: 10, 3: 8, 5: 2, 7: 1, 11: 1, 13: 1, 17: 1, 19: 1}
QBIG = 1
for p, e in PRIMES.items():
    QBIG *= p ** e
CAP = 1 << 62          # exact values above this become HUGE


def carmichael_pp(p, e):
    if p == 2:
        return 1 if e == 1 else 2 if e == 2 else 2 ** (e - 2)
    return (p - 1) * p ** (e - 1)


def pp_factors(m):
    out = {}
    for p in PRIMES:
        e = 0
        while m % p == 0:
            m //= p; e += 1
        if e:
            out[p] = e
    assert m == 1, 'modulus must divide QBIG'
    return out


class Num:
    __slots__ = ('x', 'res', 'mod')

    def __init__(self, x=None, res=None, mod=None):
        if x is not None:
            if x > CAP:
                self.x = None; self.mod = QBIG; self.res = x % QBIG
            else:
                self.x = x; self.res = None; self.mod = None
        else:
            self.x = None; self.mod = mod; self.res = res % mod

    @staticmethod
    def huge(res, mod=QBIG):
        return Num(None, res, mod)

    @property
    def exact(self):
        return self.x is not None

    def __repr__(self):
        return str(self.x) if self.exact else f'HUGE[{self.res} mod {self.mod}]'

    def m(self, k):
        """value mod k (k must divide self.mod for huge values)"""
        if self.exact:
            return self.x % k
        assert self.mod % k == 0, f'residue mod {k} unknown (have mod {self.mod})'
        return self.res % k

    def known_mod(self, k):
        return self.exact or self.mod % k == 0

    # arithmetic -----------------------------------------------------------------------------------------------
    def __add__(self, o):
        o = o if isinstance(o, Num) else Num(o)
        if self.exact and o.exact:
            return Num(self.x + o.x)
        mod = gcd(self.mod or o.mod or QBIG, o.mod or self.mod or QBIG)
        a = self.x if self.exact else self.res
        b = o.x if o.exact else o.res
        return Num.huge(a + b, mod)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Num) else Num(o)
        if self.exact and o.exact:
            return Num(self.x - o.x)
        assert o.exact, 'huge - huge is not supported'
        return Num.huge(self.res - o.x, self.mod)

    def __mul__(self, k):
        assert isinstance(k, int)
        if self.exact:
            return Num(self.x * k)
        return Num.huge(self.res * k, self.mod)

    __rmul__ = __mul__

    def divexact(self, k):
        """self / k, k | self (checked on the residue)"""
        if self.exact:
            assert self.x % k == 0
            return Num(self.x // k)
        assert self.mod % k == 0 and self.res % k == 0, f'cannot divide {self} by {k}'
        # x = res + mod*t  ->  x/k = res/k + (mod/k) t
        return Num.huge(self.res // k, self.mod // k)

    def ge(self, k):
        return (not self.exact) or self.x >= k

    def eq(self, k):
        return self.exact and self.x == k

    def __eq__(self, o):
        if isinstance(o, int):
            return self.eq(o)
        if isinstance(o, Num):
            if self.exact and o.exact:
                return self.x == o.x
            if not self.exact and not o.exact:
                return self.res % gcd(self.mod, o.mod) == o.res % gcd(self.mod, o.mod) and self.mod == o.mod
            return False
        return NotImplemented

    def __hash__(self):
        return hash((self.x, self.res, self.mod))


def pow2(e):
    """2^e as a Num"""
    if e.exact:
        if e.x <= 62:
            return Num(1 << e.x)
        return Num.huge(pow(2, e.x, QBIG), QBIG)
    # huge exponent: for every odd prime power p^k | QBIG with lambda(p^k) | e.mod we know 2^e mod p^k
    fac = PRIMES
    mod = 2 ** PRIMES[2]           # 2^e = 0 mod 2^10 since e >= 64
    crt = [(0, 2 ** PRIMES[2])]
    for p, emax in fac.items():
        if p == 2:
            continue
        best = 0
        for k in range(emax, 0, -1):
            if e.mod % carmichael_pp(p, k) == 0:
                best = k; break
        if best:
            pk = p ** best
            lam = carmichael_pp(p, best)
            crt.append((pow(2, e.res % lam, pk), pk))
    r, m = 0, 1
    for a, n in crt:
        # combine r mod m with a mod n
        t = ((a - r) * pow(m, -1, n)) % n
        r, m = r + m * t, m * n
    return Num.huge(r, m)


# the champion process in r-form (r = D-length of the accumulator token) ------------------------------------------
def H0pow(u, r):
    """u R1 rounds: r -> 2r+4, u times = (r+4) 2^u - 4"""
    return (r + 4) * 1 if False else (pow2(u) * 1 if False else None)


def r1_rounds(u, r, e=2):
    """u R1 rounds, r -> 2r + 6 - e each: (r + 6 - e) * 2^u - (6 - e)"""
    c = 6 - e
    p = pow2(u)
    if p.exact and r.exact:
        return Num((r.x + c) * p.x - c)
    if p.exact:
        return Num.huge((r.res + c) * p.x - c, r.mod)
    if r.exact:
        return Num.huge((r.x + c) * p.res - c, p.mod)
    m = gcd(p.mod, r.mod)
    return Num.huge((r.res + c) * p.res - c, m)


_TAU = {}


def tau(e=2):
    """universal residue of huge accumulators (fixed point of H1 on residues), r-form with offset e"""
    if e not in _TAU:
        x = Num(e)
        seen = []
        for _ in range(200):
            x = H(1, Num(1), x, e)
            seen.append(x)
            if len(seen) > 3 and not x.exact and seen[-2] == x and seen[-3] == x:
                break
        assert not x.exact
        _TAU[e] = x
    return _TAU[e]


def H(d, u, r, e=2):
    """apply H_d u times to r.  H_0 = one R1 round; H_d(r) = H_{d-1}^{(2r+6-2e)/3}(e).  r must be = e mod 3."""
    if u.exact and u.x == 0:
        return r
    if d == 0:
        return r1_rounds(u, r, e)
    x = r
    it = 0
    prev = []
    while True:
        if u.exact and it >= u.x:
            return x
        assert x.m(3) == e % 3, f'non-standard accumulator {x} inside H (e={e})'
        k = (x * 2 + (6 - 2 * e)).divexact(3)
        if d == 1:
            x = r1_rounds(k, Num(e), e)
        elif not k.exact or k.x >= 64:
            x = tau(e)                   # H_{d-1}^k(e) with d-1 >= 1 and k >= 64: a tower of height >= k
        else:
            x = H(d - 1 if isinstance(d, int) else 2, k, Num(e), e)
        it += 1
        if not x.exact:
            prev.append(x)
            if len(prev) >= 3 and prev[-1] == prev[-2] == prev[-3]:
                return x
        if it > 400:
            raise RuntimeError('H iteration did not stabilise')


if __name__ == '__main__':
    t = tau()
    print('tau (r-form):', t)
    B = (t - 2).divexact(3)
    print('B mod 5,7,9,16,11,13 =', [B.m(k) for k in (5, 7, 9, 16, 11, 13)])
    # BB(7) champion check: K(1^11;1;2) -> exhaustion accumulator; 2B+4 = 2^^13 3 => residues as above
