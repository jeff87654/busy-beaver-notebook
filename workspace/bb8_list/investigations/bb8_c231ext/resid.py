import idle
"""Exact residues of champ_231's final accumulator a_f.
a_f = g(w), g(w) = f^(3w+2)(1) = (5*3^(3w+2)-3)/2 with w = previous accumulator, itself g of a deep chain (depth ~ 3a+1 B1 steps).
R(Q) = a_f mod Q for the infinitely deep chain; val(k,Q) = g^k(6) mod Q (finite chain, g(6) = f^20(1) exact) for checking."""
from functools import lru_cache
from math import gcd
from sympy import factorint
def carmichael(m):
    if m == 1: return 1
    from math import lcm
    r = 1
    for p, e in factorint(m).items():
        if p == 2: l = 1 if e == 1 else 2 if e == 2 else 2 ** (e - 2)
        else: l = (p - 1) * p ** (e - 1)
        r = lcm(r, l)
    return r
def split3(m):
    t = 0
    while m % 3 == 0: m //= 3; t += 1
    return t, m
def crt(r1, m1, r2, m2):
    from sympy.ntheory.modular import crt as _c
    x = _c([m1, m2], [r1, r2]); return int(x[0]) % (m1 * m2)
def pow3_big(emod_fn, m):
    """3^e mod m for huge e (e >= anything), where emod_fn(L) gives e mod L."""
    t, mp = split3(m)
    L = carmichael(mp)
    r = pow(3, emod_fn(L), mp) if mp > 1 else 0
    return crt(0, 3 ** t, r, mp) if t else r
G1 = (5 * 3 ** 20 - 3) // 2
@lru_cache(None)
def val(k, Q):
    if k == 1: return G1 % Q
    X = 5 * pow3_big(lambda L: (3 * val(k - 1, L) + 2) % L, 2 * Q) % (2 * Q)
    return ((X - 3) // 2) % Q
DEPTH = 40
def R(Q):
    r = val(DEPTH, Q)
    assert r == val(DEPTH - 1, Q) == val(DEPTH - 2, Q), ('not stabilised', Q)
    return r
if __name__ == '__main__':
    for Q in [2, 4, 8, 16, 32, 64, 1024, 27, 81, 3**8, 5, 25, 7, 11, 13, 2**10 * 3**6 * 5**2 * 7 * 11 * 13]:
        print(Q, R(Q), [val(k, Q) for k in range(1, 9)])
    # sanity: f(x) = 3x+3 relation: R(Q) should equal g(R) consistently; and 2a+3 = 0 mod 3^K
    print('2a+3 mod 3^8:', (2 * R(3**8) + 3) % 3**8)
