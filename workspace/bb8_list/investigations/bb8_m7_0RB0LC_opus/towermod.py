"""Residues of the champion parameter B (2B+4 = 2^^^...^3 with 13 arrows, a power tower of 2s of astronomic height)."""
from math import gcd
from functools import lru_cache
def factor(n):
    f = {}; p = 2
    while p * p <= n:
        while n % p == 0: f[p] = f.get(p, 0) + 1; n //= p
        p += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f
def carmichael(n):
    if n == 1: return 1
    l = 1
    for p, k in factor(n).items():
        if p == 2: c = 1 if k == 1 else (2 if k == 2 else 2 ** (k - 2))
        else: c = (p - 1) * p ** (k - 1)
        l = l * c // gcd(l, c)
    return l
@lru_cache(maxsize=None)
def tower(m):
    """2^2^2^...^2 (astronomically tall) mod m"""
    if m == 1: return 0
    lam = carmichael(m)
    e = tower(lam) + lam * 200          # exponent is astronomically large: same residue mod lam, and >= 200
    return pow(2, e, m)
def B_mod(m):
    t = tower(2 * m)                    # 2B+4 mod 2m
    assert (t - 4) % 2 == 0
    return ((t - 4) // 2) % m
if __name__ == '__main__':
    for m in (5, 7, 9, 8, 504, 98, 3528, 14112, 2016 * 7 * 5):
        print(m, B_mod(m), (12 * B_mod(m) + 7) % m)
