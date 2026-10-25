# towmod.py (c7check): residue of a power tower of 2s of large height mod m, and the derived accumulator residue.
# tower(h) = 2^2^...^2 (h twos).  For h large, tower(h) mod m is constant; we iterate until stable.
import idle
from sympy import totient
def tw(h, m):
    """tower of h twos mod m, exact using generalized Euler (valid when exponent >= log2 m)."""
    if m == 1: return 0
    if h == 1: return 2 % m
    if h <= 4:
        v = 2
        for _ in range(h-1): v = 2**v
        return v % m
    ph = int(totient(m))
    e = tw(h-1, ph)
    return pow(2, e + ph*40, m)  # exponent huge (>= 65536 > log2 m) so add multiple of ph
def stable(m, H=60):
    vals=[tw(h, m) for h in range(H-5, H)]
    assert len(set(vals))==1, (m, vals)
    return vals[0]
def Rres(m):
    """R mod m where 2R+4 = huge power tower of 2s."""
    S = stable(2*m)
    assert (S-4) % 2 == 0
    return ((S-4)//2) % m
if __name__ == "__main__":
    import sys
    for m in [5,25,125,625,5**10,5**13,3600,2520,25200,2**10*3**6, 5**13*2**10*3**6*7*11*13]:
        print(m, Rres(m))
