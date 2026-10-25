"""Residues of 2^^n (n large, stabilized) and of the accumulator R = (2^^n - 4)/2.  python tower.py"""
import idle
from sympy import totient
def tower_mod(m, h=60):
    # 2^^h mod m, h large
    if m == 1: return 0
    if h == 0: return 1 % m
    e = tower_mod(int(totient(m)), h - 1)
    # 2^^(h-1) is huge, so exponent = e + k*phi(m) with value >= log2(m): add phi(m) if needed
    ph = int(totient(m))
    while e < 64: e += ph
    return pow(2, e, m)
if __name__ == '__main__':
    M = 2 * 5**14 * 2**12 * 3**8 * 7**3 * 11 * 13
    T = tower_mod(M); T2 = tower_mod(M, 80)
    assert T == T2
    R = (T - 4) // 2 % (M // 2)
    print('R_* mod 5^14 =', R % 5**14, ' mod 5^10 =', R % 5**10, ' mod 3600 =', R % 3600, ' mod 2^10 =', R % 2**10, ' mod 3^6 =', R % 3**6)
