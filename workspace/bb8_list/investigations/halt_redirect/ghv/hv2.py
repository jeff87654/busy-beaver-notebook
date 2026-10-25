"""Huge values with exact 2-adic part (gh0LH verifier).
A Huge X is astronomically large; s2 (a rational with odd denominator) satisfies X = s2 (mod 2^K) for a K far larger than
any number of halvings we ever perform (tower values: 6*2^N - 6 = -6 mod 2^N); `odd` is X mod mo, mo | MO (odd part of M).
Arithmetic fails loudly (Unknown) when a needed residue is not determined."""
from fractions import Fraction
from math import gcd
MOF = {3: 20, 5: 12, 7: 8, 11: 1, 13: 1, 17: 1, 19: 1}     # odd modulus, lambda-closed (odd parts of lambda divide MO)
MO = 1
for _p, _e in MOF.items(): MO *= _p ** _e
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
def carmf(f):
    out = 1
    for p, e in f.items():
        l = (2 ** (e - 2) if e > 2 else e) if p == 2 else (p - 1) * p ** (e - 1)
        out = out * l // gcd(out, l)
    return out
LAMO = carmf(MOF)
_lo = LAMO
while _lo % 2 == 0: _lo //= 2
assert MO % _lo == 0, 'MO not lambda-closed'
CAP = 1 << 60
class Unknown(Exception): pass
def m2(s, k):
    """s (Fraction with odd denominator) mod 2^k"""
    s = Fraction(s)
    if s.denominator % 2 == 0: raise Unknown('even denominator in 2-adic part')
    return (s.numerator * pow(s.denominator, -1, 2 ** k)) % 2 ** k
class Huge:
    __slots__ = ('s2', 'odd', 'mo')
    def __init__(self, s2, odd, mo=MO):
        s2 = Fraction(s2)
        if s2.denominator % 2 == 0: raise Unknown(f'2-adic part {s2} not a 2-adic integer')
        assert MO % mo == 0
        self.s2 = s2; self.mo = mo; self.odd = odd % mo
    def key(self): return (self.s2, self.odd, self.mo)
    def __eq__(self, o): return isinstance(o, Huge) and o.key() == self.key()
    def __hash__(self): return hash(self.key())
    def __repr__(self):
        s = self.s2 if self.s2.denominator == 1 else f'{self.s2}'
        return f'H[{s}|{self.odd % 315}]' if self.mo % 315 == 0 else f'H[{s}|{self.odd}/{self.mo}]'
    def mod(self, k):
        a = 0
        while k % 2 == 0: k //= 2; a += 1
        if self.mo % k: raise Unknown(f'odd residue mod {k} unknown (mo={self.mo})')
        if a == 0: return self.odd % k
        r2 = m2(self.s2, a); ro = self.odd % k; K = 2 ** a
        # CRT
        return (r2 + K * (((ro - r2) * pow(K, -1, k)) % k)) % (K * k) if k > 1 else r2
def isH(x): return isinstance(x, Huge)
def mk(x):
    return Huge(x, x % MO) if (not isH(x) and x > CAP) else x
def mod(x, k): return x.mod(k) if isH(x) else x % k
def lin(c, x, d):
    """c*x + d with integer c, d"""
    if isH(x): return Huge(c * x.s2 + d, c * x.odd + d, x.mo)
    return mk(c * x + d)
def pow2_huge(n):
    """2^n mod MO for huge n (needs n mod LAMO)"""
    return pow(2, mod(n, LAMO), MO)
def r1(a, r):
    """G R1 iterated: a = 3n+1 -> 1, r -> 2^n (r+6) - 6"""
    if mod(a, 3) != 1: raise AssertionError('r1 needs a = 1 mod 3')
    if not isH(a):
        n = (a - 1) // 3
        if not isH(r) and n < 64 and (r + 6) << n <= CAP: return ((r + 6) << n) - 6
        if not isH(r): return Huge(2 ** n * (r + 6) - 6 if n < 4096 else -6, pow(2, n, MO) * (r + 6) - 6)
        return Huge((2 ** n * (r.s2 + 6) - 6) if n < 4096 else -6, pow(2, n, MO) * (r.odd + 6) - 6, r.mo)
    n = lin(1, a, -1)                       # 3n; need n mod LAMO -> a mod 3*LAMO
    nres = (mod(a, 3 * LAMO) - 1) // 3
    p = pow(2, nres % LAMO, MO)
    if isH(r): return Huge(-6, p * (r.odd + 6) - 6, r.mo)
    return Huge(-6, p * (r + 6) - 6)
def fixpoint(f, x0):
    x = x0
    for i in range(300):
        y = f(x)
        if y == x: return x, i
        x = y
    raise RuntimeError('no fixed point')
U, _it = fixpoint(lambda x: r1(lin(2, x, 7), 0), Huge(0, 0))
if __name__ == '__main__':
    M0 = 2**10 * 3**8 * 5**2 * 7 * 11 * 13 * 17 * 19
    print('U', U, 'iters', _it, 'U mod 2^10*3^8*5^2*7*11*13*17*19 =', U.mod(M0), ' (lead: 49612750485498)')
