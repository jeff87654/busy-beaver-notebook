"""Universal residues of tall towers 2^2^2^... and of the record's b-form accumulators (2b+4 = tower)."""
from math import gcd
def carm(m):
    # Carmichael lambda
    from sympy import factorint
    l = 1
    for p, e in factorint(m).items():
        if p == 2:
            v = 1 if e == 1 else 2 if e == 2 else 2 ** (e - 2)
        else:
            v = (p - 1) * p ** (e - 1)
        l = l * v // gcd(l, v)
    return l
def tower_mod(m, height=60):
    """2^2^...^2 (height levels, huge) mod m, valid for tall towers"""
    if m == 1:
        return 0
    if height == 0:
        return 2 % m
    l = carm(m)
    e = tower_mod(l, height - 1)
    # exponent is huge: use e + l*k with e+l*k >= 64
    e2 = e
    while e2 < 64:
        e2 += l
    return pow(2, e2, m)
def b_mod(m):
    T = tower_mod(2 * m)
    assert (T - 4) % 2 == 0
    return ((T - 4) // 2) % m
if __name__ == '__main__':
    for m in (8, 3, 5, 7, 11, 840, 25, 125, 625, 3125, 2**12 * 5**8):
        print(m, b_mod(m))
