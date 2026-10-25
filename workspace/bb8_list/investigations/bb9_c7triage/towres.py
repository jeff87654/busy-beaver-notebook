import idle
"""towres.py: stable residue of R_* = (2^^N - 4)/2 for huge N, modulo m (2^^N mod 2m computed by iterated Euler)."""
from sympy import totient
def tow(m, h=60):
    # 2^^h mod m, h large enough to stabilise
    if m == 1: return 0
    if h == 0: return 1 % m
    e = tow(int(totient(m)), h - 1)
    # 2^^(h-1) is huge, so exponent = e + k*phi with exponent >= log2(m)
    ph = int(totient(m)); ex = e
    while ex < 64: ex += ph
    return pow(2, ex, m)
def Rstar(m): return ((tow(2 * m) - 4) // 2) % m
if __name__ == '__main__':
    for m in [3600, 125, 625, 3125, 5**6, 5**7, 2520, 7]:
        print(m, Rstar(m))
