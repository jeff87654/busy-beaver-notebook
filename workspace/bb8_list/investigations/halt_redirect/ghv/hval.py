"""Exact-or-huge values for the gh0LH verifier (independent of numres.py).
M = 2^10 3^8 5^2 7 11 13 17 19 is lambda-closed; a Huge is astronomically large and carries its residue mod a divisor
`mod` of M (mod shrinks when a literal stage halves a huge value). Operations fail loudly if a needed residue is unknown."""
from math import gcd
M = 2**10 * 3**8 * 5**2 * 7 * 11 * 13 * 17 * 19
MO = M // 2**10
def carm(n):
    f, p, out = {}, 2, 1
    while p * p <= n:
        while n % p == 0: f[p] = f.get(p, 0) + 1; n //= p
        p += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    for p, e in f.items():
        l = (2 ** (e - 2) if e > 2 else e) if p == 2 else (p - 1) * p ** (e - 1)
        out = out * l // gcd(out, l)
    return out
LAM = carm(M); LAMO = carm(MO)
assert M % LAM == 0 and M % (3 * LAM) == 0
CAP = 1 << 60
class Unknown(Exception): pass
class Huge:
    __slots__ = ('res', 'mod')
    def __init__(self, res, mod=M):
        assert M % mod == 0
        self.res = res % mod; self.mod = mod
    def __repr__(self): return f'H[{self.res % 2520}]' if self.mod % 2520 == 0 else f'H[{self.res % self.mod}/{self.mod}]'
    def __eq__(self, o): return isinstance(o, Huge) and o.res == self.res and o.mod == self.mod
    def __hash__(self): return hash(('H', self.res, self.mod))
def mk(x):
    return Huge(x) if (not isinstance(x, Huge) and x > CAP) else x
def mod(x, k):
    if isinstance(x, Huge):
        if x.mod % k: raise Unknown(f'residue mod {k} unknown (have mod {x.mod})')
        return x.res % k
    return x % k
def lin(c, x, d):
    """c*x + d (c integer)"""
    if isinstance(x, Huge): return Huge(c * x.res + d, x.mod)
    return mk(c * x + d)
def r1(a, r):
    """R1 iterated: a = 3n+1 -> 1, r -> 2^n (r+6) - 6"""
    assert mod(a, 3) == 1
    if not isinstance(a, Huge):
        n = (a - 1) // 3
        if not isinstance(r, Huge) and n < 64 and (r + 6) << n <= CAP:
            return ((r + 6) << n) - 6
        rr, rm = (r.res, r.mod) if isinstance(r, Huge) else (r, M)
        return Huge(pow(2, n, M) * (rr + 6) - 6, rm)
    if a.mod % (3 * LAMO) or (a.mod % (3 * LAM)):
        raise Unknown(f'exponent residue unknown: a mod {a.mod}')
    nres = ((a.res - 1) % (3 * LAM)) // 3
    rr, rm = (r.res, r.mod) if isinstance(r, Huge) else (r, M)
    p_odd = pow(2, nres % LAMO, MO)
    inv = pow(2**10, -1, MO)
    p = (2**10 * ((p_odd * inv) % MO)) % M      # 2^n mod M for huge n: 0 mod 2^10, p_odd mod MO
    return Huge(p * (rr + 6) - 6, rm)
def fixpoint(f):
    x = Huge(0)
    for i in range(200):
        y = f(x)
        if y == x: return x, i
        x = y
    raise RuntimeError('no fixed point')
U, _it = fixpoint(lambda x: r1(lin(2, x, 7), 0))          # G-frame: refill 2r+7, count down from r = 0
if __name__ == '__main__':
    print('M', M, 'LAM', LAM, 'U', U.res, 'iters', _it, 'U mod 2520', U.res % 2520)
