"""num.py -- exact-or-huge numbers for the symbolic engine.

A value is a Python int (exact; kept only while < LIM) or H(r): an integer >= LIM known modulo M.
M is lambda-closed with a factor 3: lambda(M) divides M/3, so for a huge x with residue r the R1
iteration count v = (x - e)/3 is known modulo M/3, which determines 2^v modulo M (v >= 20).
"""
from math import gcd

LIM = 1 << 62
PRIMES = {2: 20, 3: 4, 5: 2, 7: 2, 11: 1, 13: 1, 17: 1, 19: 1}
M = 1
for p, e in PRIMES.items():
    M *= p ** e
M2 = 2 ** PRIMES[2]
MO = M // M2


def carmichael(n):
    def lam_pp(p, e):
        if p == 2:
            return 1 if e == 1 else 2 if e == 2 else 2 ** (e - 2)
        return (p - 1) * p ** (e - 1)
    res = 1
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            e = 0
            while m % p == 0:
                m //= p; e += 1
            l = lam_pp(p, e)
            res = res * l // gcd(res, l)
        p += 1
    if m > 1:
        l = m - 1
        res = res * l // gcd(res, l)
    return res


LAM = carmichael(M)
LAMO = carmichael(MO)
assert (M // 3) % LAM == 0, 'M not lambda-closed'
assert M % LAMO == 0


class H:
    __slots__ = ('r',)

    def __init__(self, r):
        self.r = r % M

    def __eq__(self, o):
        return isinstance(o, H) and o.r == self.r

    def __hash__(self):
        return hash(('H', self.r))

    def __repr__(self):
        return 'H%d' % (self.r % 1000003)


def is_huge(v):
    return isinstance(v, H)


def norm(v):
    if isinstance(v, int) and v >= LIM and not EXACT:
        return H(v)
    return v


def add(v, c):
    if isinstance(v, H):
        return H(v.r + c)
    return norm(v + c)


def dbl_add(v, c):
    if isinstance(v, H):
        return H(2 * v.r + c)
    return norm(2 * v + c)


def res(v, m):
    """residue of v modulo m (m must divide M for huge v)"""
    if isinstance(v, H):
        assert M % m == 0, m
        return v.r % m
    return v % m


def mod3(v):
    return res(v, 3)


def ge(v, c):
    if isinstance(v, H):
        return True
    return v >= c


def pow2_res(vres_mod_m3):
    """2^v mod M for a huge exponent v (v >= 20) given v mod M/3"""
    a2 = 0  # mod 2^20
    ao = pow(2, vres_mod_m3 % LAMO, MO)
    # CRT: x = 0 mod M2, x = ao mod MO
    inv = pow(M2, -1, MO)
    return (M2 * ((ao * inv) % MO)) % M


EXACT = False   # testing only: compute everything with big integers


def r1star(x, y):
    """iterate R1 on [.., x, 0, y] while x >= 3: returns (end token, new accumulator)"""
    e = mod3(x)
    xe = {1: 1, 0: 0, 2: 2}[e]
    if EXACT and isinstance(x, int) and isinstance(y, int):
        v = (x - xe) // 3
        if v > 400000:
            raise OverflowError("exact mode too big")
        return xe, (y + 8) * (1 << v) - 8
    if isinstance(x, int):
        v = (x - xe) // 3
        if v == 0:
            return xe, y
        if isinstance(y, int) and v < 62:
            return xe, norm((y + 8) * (1 << v) - 8)
        if v >= 20:
            p = pow(2, v, M)
        else:
            p = pow(2, v, M)
        yr = res(y, M) if isinstance(y, H) else y % M
        return xe, H(((yr + 8) * p - 8) % M)
    # huge x: v huge
    vres = ((x.r - xe) // 3) % (M // 3) if (x.r - xe) % 3 == 0 else None
    assert vres is not None
    p = pow2_res(vres)
    yr = y.r if isinstance(y, H) else y % M
    return xe, H(((yr + 8) * p - 8) % M)


def key(v):
    return ('H', v.r) if isinstance(v, H) else v
