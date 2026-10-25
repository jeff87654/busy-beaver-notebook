"""tower.py: independent residues.
(1) Deep accumulator token r*: one cycle at depth 0 maps r -> 6*2^((2r+4)/3) - 5 (R2 then (2r+4)/3 R1 steps from r = 1:
    h(x) = 2x+5, h^m(1) = 6*2^m - 5).  A deep clearing ends with such a step whose input is itself the output of one, so
    r* = 3*2^X - 5 with X = (2r'+7)/3 = 2^(X'+1) - 1, X' of the same form: an infinitely tall tower, residues stable.
(2) B: 2B+4 = 2^^^37 3 (37 arrows) = 2^T with T a tower of 2s (T >= 2^65536), so B = 2^(T-1) - 2."""
from sympy import factorint
from math import gcd
def carm(m):
    if m == 1: return 1
    f = factorint(m); l = 1
    for p, e in f.items():
        if p == 2: t = 1 if e == 1 else (2 if e == 2 else 2 ** (e - 2))
        else: t = (p - 1) * p ** (e - 1)
        l = l * t // gcd(l, t)
    return l
def pow2_big(e_mod_lam, m):
    """2^E mod m for an astronomically large E with E = e_mod_lam (mod lambda(m))"""
    lam = carm(m); e = e_mod_lam % lam
    e += lam * ((200 // lam) + 1)
    return pow(2, e, m)
def X_mod(m):
    """X = 2^(X+1) - 1 (infinite tower) mod m"""
    if m == 1: return 0
    lam = carm(m)
    xl = X_mod(lam)
    return (pow2_big(xl + 1, m) - 1) % m
def rstar(m):
    lam = carm(m)
    return (3 * pow2_big(X_mod(lam), m) - 5) % m
def T_mod(m):
    """T = power tower of 2s (very tall) mod m: T = 2^T'"""
    if m == 1: return 0
    return pow2_big(T_mod(carm(m)), m)
def B_mod(m):
    lam = carm(m)
    return (pow2_big((T_mod(lam) - 1), m) - 2) % m
if __name__ == '__main__':
    M = 54305848396800
    print('r* - 1 mod', M, '=', (rstar(M) - 1) % M, ' (lead: 49612750485498)')
    MB = 18101949465600
    print('B mod', MB, '=', B_mod(MB), ' (lead: 16537583495166)')
    for m in (3, 9, 27, 8, 16, 32, 5, 25, 7, 13, 11, 720, 5040, 2520, 1200):
        print(m, 'r*', rstar(m), 'B', B_mod(m))
