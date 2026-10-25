import idle
"""orbit.py: own computation of the stable residue of every tower accumulator and of h003's real top-level orbit.
Every accumulator X here satisfies 2X+4 = (pure power tower of 2s of huge height) [B: 2B+4 = 2^^13 3; U_j: 2U_j(x)+4 =
2^^(j+1)(2x+4)], so X = (T-4)/2 with T = 2^^N mod 2m, N huge.  Stable value of 2^^N mod m: m = 2^a m' (m' odd):
  mod 2^a: 0 (N large);  mod m': 2^(E mod ord) with E = 2^^(N-1) mod lambda(m') (recursively; 2 is a unit mod m').
CRT.  No '+phi' adjustments are needed with this split.  Cross-check: direct towers 2^^h mod m for h = 6..12 computed
with exact repeated squaring by exponent reduction (must agree from small h on)."""
import sys
from sympy import factorint
from sympy.ntheory.modular import crt
from math import gcd

def carmichael(n):
    if n == 1: return 1
    l = 1
    for p, e in factorint(n).items():
        if p == 2: c = 1 if e == 1 else (2 if e == 2 else 2 ** (e - 2))
        else: c = (p - 1) * p ** (e - 1)
        l = l * c // gcd(l, c)
    return l

def tow(m):
    """2^^N mod m for N -> infinity (stable)."""
    if m == 1: return 0
    a = 0; mo = m
    while mo % 2 == 0: mo //= 2; a += 1
    if mo == 1: return 0
    e = tow(carmichael(mo))
    v = pow(2, e, mo)
    if a == 0: return v
    r, M = crt([2 ** a, mo], [0, v])
    return int(r)

def tow_direct(h, m):
    """2^^h mod m exactly, h small (2^^1 = 2), by the generalized Euler rule with a size guard."""
    # returns (value mod m, value capped at 2^64 for size)
    if h == 1: return 2 % m, 2
    lam = carmichael(m) if m > 1 else 1
    e_mod, e_cap = tow_direct(h - 1, lam * 64)  # enough to know e mod lam and whether e >= 64
    if e_cap < 64: return pow(2, e_cap, m), 2 ** e_cap
    # e >= 64 > max exponent of 2 in m: 2^e mod m = 2^(64 + (e-64) mod lam) mod m works when lam | period and e>=a
    e_eff = 64 + ((e_mod - 64) % lam)
    return pow(2, e_eff, m), 1 << 64

def Rstar(m):
    t = tow(2 * m)
    assert (t - 4) % 2 == 0
    return ((t - 4) // 2) % m

RULE = {1: (9, 36), 4: (3, -2), 3: (3, 16)}

if __name__ == '__main__':
    for m in [3600, 125, 625, 5 ** 13, 2520, 18000, 2 ** 5 * 3 ** 4 * 5 ** 14]:
        print('R* mod', m, '=', Rstar(m))
    for m in [3600, 5 ** 8, 2 ** 6 * 3 ** 4 * 5 ** 6 * 7]:
        d = [(tow_direct(h, 2 * m)[0] - 4) // 2 % m for h in range(5, 12)]
        print('direct check mod', m, d, 'stable', Rstar(m))
    for k in [20, 40, 80, 120]:
        P = 5 ** k
        Rs = Rstar(P)
        K = (12 * Rs + 27) % P; mod = P; res = []; Ks = []
        while True:
            r = K % 5; res.append(r); Ks.append(K)
            if r not in RULE: break
            a, c = RULE[r]; num = a * K + 60 * Rs + c; assert num % 5 == 0
            mod //= 5; K = (num // 5) % mod
        print('5^%d: residues of K0,K1,..: %s  (exit at index %d); exit K mod 5^%d = %d' % (k, res, len(res) - 1, k - len(res) + 1, K))
    # mod 2^8 3^5 (5 is a unit there) along the real branch sequence: parity / mod 3 of the exit K and of L0 = 3K-2
    P = 5 ** 40; Rs = Rstar(P); K = (12 * Rs + 27) % P; br = []
    for _ in range(6):
        r = K % 5; br.append(r)
        if r not in RULE: break
        a, c = RULE[r]; K = (a * K + 60 * Rs + c) // 5
    m2 = 2 ** 8 * 3 ** 5; R2 = Rstar(m2); K = (12 * R2 + 27) % m2; seq = [K]; inv5 = pow(5, -1, m2)
    for r in br[:-1]:
        a, c = RULE[r]; K = (a * K + 60 * R2 + c) * inv5 % m2; seq.append(K)
    print('branches', br, 'K_i mod 256, mod 243:', [(x % 256, x % 243) for x in seq])
    print('exit K4: mod 2 =', seq[-1] % 2, ' mod 3 =', seq[-1] % 3, '; L0 = 3K4-2: mod 2 =', (3 * seq[-1] - 2) % 2, ' mod 3 =', (3 * seq[-1] - 2) % 3)
