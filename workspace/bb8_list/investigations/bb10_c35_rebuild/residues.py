"""Exact residues of the tower-type accumulators of the run (the lead's T(m) method).
Every event accumulator s satisfies 2s + 4 = 2^E with E itself a tall power tower of 2s (champion clearings: Coq
U_closed 2U_j(x)+4 = 2^^(j+1)(2x+4); R1 chains from a reset end with 2s+4 = 2^(a+2), a = 2s'+2).  So 2s+4 = T(m) mod m,
T(m) = stable residue of an infinite 2-tower.  Conventions: s = the K-family counter b; my r-token r = 3s+1 (the D-length
of the b-token at a K-moment with tail D2); follow2's R (template c35, e=0, tail D4, one round later) = 3s;
the BB(8) record's final accumulator B is such an s."""
from numres import tau


def phi(n):
    r = n; m = n; p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


def T(m):
    return 0 if m == 1 else pow(2, T(phi(m)) + phi(m), m)


def s_mod(m):
    """s mod m from 2s+4 = T(2m) mod 2m"""
    t = T(2 * m)
    assert t % 2 == 0
    return ((t - 4) // 2) % m


if __name__ == '__main__':
    for m in (11, 8, 3, 5, 7, 9, 16, 25, 840, 27720):
        print(f's mod {m:6d} = {s_mod(m):6d}   r = 3s+1 mod {m} = {(3 * s_mod(m) + 1) % m}   R = 3s mod {m} = {3 * s_mod(m) % m}')
    B = (tau(2) - 2).divexact(3)
    print('numres B mod 27720 =', B.m(27720), ' T-method:', s_mod(27720))
    print('follow2 universal R (49612750485498) mod 11 =', 49612750485498 % 11, ', /3 =', 49612750485498 // 3, '= B residue 16537583495166:', 49612750485498 // 3 == 16537583495166)
    s = s_mod(27720)
    r = 3 * s + 1
    print('C0 = 2 r1 + 5 mod 11 =', (2 * r + 5) % 11, '   C\' = 2r - r\' - 2 mod 11 =', (2 * r - r - 2) % 11, ' mod 8 =', (2 * r - r - 2) % 8)
    print('x = 2r\'+3 mod 12 =', (2 * r + 3) % 12, '  r mod 4 =', r % 4)
