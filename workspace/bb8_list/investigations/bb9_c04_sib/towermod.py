"""towermod.py : residues of the BB(7)-engine accumulator B (2B+4 = 2^^^...^ = arrow(13, 2, 3), a power tower of 2s of
astronomical height) and of derived quantities.  tower2(m) = value of a tall power tower of 2s mod m (stable for any
height >= ~log2(m)+5); uses 2^e mod m with e = tower2(phi(m)) + phi(m)*K (generalized Euler, e large)."""
from math import gcd
from functools import lru_cache
def phi(m):
    r, n, p = m, m, 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0: n //= p
            r -= r // p
        p += 1
    if n > 1: r -= r // n
    return r
@lru_cache(None)
def tower2(m):
    if m == 1: return 0
    f = phi(m); e = tower2(f) + f * 64      # exponent >= 64*phi(m) > log2(m): valid for the generalized Euler theorem
    return pow(2, e, m)
def B_mod(m):
    """B mod m, from 2B+4 = T (a tall tower of 2s): B = (T-4)/2, need T mod 2m"""
    T = tower2(2 * m)
    return ((T - 4) % (2 * m)) // 2
if __name__ == '__main__':
    import sys
    print('B mod 5 =', B_mod(5), ' B mod 2520 =', B_mod(2520), ' B mod 11 =', B_mod(11))
    for K in range(1, 16):
        b = B_mod(5 ** K); n = (12 * b + 25) % 5 ** K
        print('K=%d  B mod 5^K = %d   n = 12B+25 mod 5^K = %d  (base5 %s)' % (K, b, n, ''.join(str(n // 5 ** i % 5) for i in range(K))[::-1]))
