"""stable residue of the 2-power tower mod m (independent of numres)."""
from sympy import totient
from functools import lru_cache
import sys
def carm(m):
    from sympy.ntheory import reduced_totient
    return int(reduced_totient(m))
def tower_mod(m, h=200):
    # residue of 2^2^...^2 (height h, h large) mod m via generalized Euler: 2^x = 2^(x mod lam + lam) when x >= log2 m
    if m == 1: return 0
    lam = carm(m)
    e = tower_mod(lam, h - 1)
    return pow(2, e + lam * 64, m)  # exponent huge: add multiple of lam to stay above the 2-adic threshold
if __name__ == '__main__':
    Q = 2**10 * 3**8 * 5**2 * 7 * 11 * 13 * 17 * 19
    T = tower_mod(Q)
    print('Q', Q, 'T mod Q', T)
    for h in range(3, 8):
        pass
    R = 49612750485498
    print('lead R', R, 'R mod 2520', R % 2520, 'R mod 21', R % 21, 'mod 42', R % 42)
    for c in range(-20, 21):
        for mul in (1, 2, 3, 4, 6):
            if (mul * T + c - R) % Q == 0: print('R = %d*T + %d' % (mul, c))
