"""Reset sequence of 1RB1RH_0LC0LF_1LE1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---.
Z(k,n) = 0^inf (1110)^k 11 (10)^n E> 0^inf.  digit: Z(k+1,n) -> Z(k,9n+13).
Z(0,n) -> 0^inf (10)^m E>, m = 3n+4; m odd -> Z((m+1)/2, 2); m even -> halt.
From the blank tape: Z(1,2) at step 31, so k_0 = 1.
F(k,n) = f^k(n), f(n) = 9n+13;  F(k,2) = (29*9^k - 13)/8.
"""
from math import log10
def F(k, n):
    for _ in range(k): n = 9 * n + 13
    return n
def Fm(k, n, m):
    n %= m
    for _ in range(k): n = (9 * n + 13) % m
    return n
def Fc(k, M):
    x = 29 * pow(9, k, 8 * M) - 13
    assert x % 8 == 0
    return (x // 8) % M
assert all(F(k, 2) == (29 * 9**k - 13) // 8 for k in range(30))
assert all(Fc(k, 2**e) == F(k, 2) % 2**e for k in range(40) for e in range(1, 12))
# period: f^(2^e) = id mod 2^e
for e in range(1, 12):
    M = 2**e
    assert all(Fm(M, x, M) == x for x in range(M)), e
k0 = 1
N0 = F(k0, 2); m0 = 3 * N0 + 4
print('k0 = 1, N0 =', N0, 'm0 =', m0)
k1 = (m0 + 1) // 2
N1 = F(k1, 2); m1 = 3 * N1 + 4
assert m1 % 2 == 1
k2 = (m1 + 1) // 2
assert k2 == (87 * 9**49 + 1) // 16
print('k1 =', k1, '; N1 = F(49,2) =', N1, '(%d digits)' % len(str(N1)))
print('k2 =', k2, ' log10 = %.6f' % log10(k2))
# exact-precision chain mod 2^J
J = 64
M = 2**(J + 1)
N2 = (29 * pow(9, k2, 8 * M) - 13) // 8 % M   # N2 mod 2^(J+1)
assert (29 * pow(9, k2, 8 * M) - 13) % 8 == 0
print('N2 mod 2^8 =', N2 % 256, 'odd' if N2 % 2 else 'EVEN')
k3 = ((3 * N2 + 5) // 2) % 2**J   # valid mod 2^J
N3 = Fc(k3 % 2**(J - 1), 2**(J - 1))  # period 2^(J-1) mod 2^(J-1)
print('k3 mod 2^8 =', k3 % 256, '; N3 mod 2^8 =', N3 % 256, 'odd' if N3 % 2 else 'EVEN')
k4 = ((3 * N3 + 5) // 2) % 2**(J - 2)
N4 = Fc(k4 % 2**(J - 3), 2**(J - 3))
print('k4 mod 2^8 =', k4 % 256, '; N4 mod 2^8 =', N4 % 256, 'odd' if N4 % 2 else 'EVEN')
k5 = ((3 * N4 + 5) // 2) % 2**(J - 4)
N5 = Fc(k5 % 2**(J - 5), 2**(J - 5))
print('k5 mod 2^8 =', k5 % 256, '; N5 mod 2^8 =', N5 % 256, 'odd' if N5 % 2 else 'EVEN -> m5 even -> HALT')
# low-precision chain used by the Coq proof
r1 = Fm(49, 2, 32); c2 = ((3 * r1 + 5) // 2) % 16
r2 = Fm(c2, 2, 16); c3 = ((3 * r2 + 5) // 2) % 8
r3 = Fm(c3, 2, 8); c4 = ((3 * r3 + 5) // 2) % 4
r4 = Fm(c4, 2, 4); c5 = ((3 * r4 + 5) // 2) % 2
r5 = Fm(c5, 2, 2)
print('Coq chain: N1 mod 32 = %d, k2 mod 16 = %d, N2 mod 16 = %d, k3 mod 8 = %d, N3 mod 8 = %d, k4 mod 4 = %d, '
      'N4 mod 4 = %d, k5 mod 2 = %d, N5 mod 2 = %d' % (r1, c2, r2, c3, r3, c4, r4, c5, r5))
assert (k2 % 16, k3 % 8, k4 % 4, k5 % 2) == (c2, c3, c4, c5)
# magnitudes
L3 = k2 * log10(9) + log10(87 / 16)          # log10 k3
print('log10 k3 = %.6e' % L3)
# log10 k4 = k3*log10 9 + log10(87/16) ; log10 log10 k4 = log10 k3 + log10(log10 9) (+ negligible)
LL4 = L3 + log10(log10(9))
LLL5 = LL4 + log10(log10(9))
LLLL_sigma = LLL5 + log10(log10(9))
print('log10 log10 k4 = %.6e, log10^3 k5 = %.6e, log10^4 sigma = %.6e' % (LL4, LLL5, LLLL_sigma))
print('sigma = (261*9^k5 + 75)/16  ~  10^10^10^10^(%.4e) = 10^^5 applied to 10^%.4f' % (LLLL_sigma, log10(LLLL_sigma)))
