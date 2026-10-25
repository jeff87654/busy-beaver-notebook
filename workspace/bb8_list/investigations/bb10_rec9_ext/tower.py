"""Residues of tall towers of 2s (2^2^...^2, height >> log* m): T mod m, by recursive Carmichael lambda.
R1 = R2 = (3T - 8)/2 for the BB(9) record's accumulators (2B+4 = 2^^13 3 and 2b'+4 = 2^(12B-9 arrows) 8 are both
towers of 2s).  Usage: python tower.py M  -> prints T mod M and (3T-8)/2 mod M (for odd parts), etc."""
import sys
from math import gcd


def factorint(m):
    out, p = {}, 2
    while p * p <= m:
        while m % p == 0:
            out[p] = out.get(p, 0) + 1
            m //= p
        p += 1
    if m > 1:
        out[m] = out.get(m, 0) + 1
    return out


def carmichael(m):
    if m == 1:
        return 1
    lam = 1
    for p, e in factorint(m).items():
        if p == 2:
            l = 1 if e == 1 else 2 if e == 2 else 2 ** (e - 2)
        else:
            l = (p - 1) * p ** (e - 1)
        lam = lam * l // gcd(lam, l)
    return lam


def tower_mod(m):
    """stable value of 2^^h mod m for large h"""
    if m == 1:
        return 0
    lam = carmichael(m)
    e = tower_mod(lam)
    # the true exponent is huge (>= 64): use e + lam*k with e' >= 64
    while e < 64:
        e += lam
    return pow(2, e, m)


def acc_mod(m):
    """(3T - 8)/2 mod m"""
    t = tower_mod(2 * m)
    return ((3 * t - 8) // 2) % m if (3 * t - 8) % 2 == 0 else None


if __name__ == '__main__':
    m = int(sys.argv[1])
    print('T mod', m, '=', tower_mod(m))
    print('R1 = (3T-8)/2 mod', m, '=', acc_mod(m))
