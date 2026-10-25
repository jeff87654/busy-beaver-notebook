"""Residues of the BB(9) record's parameters modulo arbitrary n.
2B+4 = 2 ^(13 arrows) 3 is a power tower of 2s of astronomically large height, so modulo n it equals the stable
value of the infinite tower 2^2^2^... mod n (computed by the totient recursion).  B = (T - 4)/2."""
from math import gcd
from sympy import totient

def tower2(n):
    """2^2^2^... (height -> infinity) mod n, as an integer in [0, n)"""
    if n == 1:
        return 0
    ph = int(totient(n))
    e = tower2(ph)
    # exponent is astronomically large: use e + ph (exponent >= log2 n), valid for any n
    return pow(2, e + ph, n)

def B_mod(n):
    """B mod n with 2B + 4 = T: compute T mod 2n then halve"""
    T = tower2(2 * n)
    assert (T - 4) % 2 == 0
    return ((T - 4) // 2) % n

if __name__ == '__main__':
    print('check vs numres: B mod 18101949465600 =', B_mod(18101949465600), '(expect 16537583495166)')
    for j in range(1, 13):
        print(j, 5 ** j, B_mod(5 ** j))
