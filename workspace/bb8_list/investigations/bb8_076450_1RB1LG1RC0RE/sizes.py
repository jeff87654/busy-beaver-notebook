"""Exact closed forms and magnitudes for the halting run of 1RB1LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RC1LG_---0LH_1RA1LF."""
from fractions import Fraction as Fr
from math import log10
import mpmath as mp
mp.mp.dps = 50

def N_of(n0, K):            # n after K digits from n0:  n -> 4n+2
    return ((3*n0 + 2) * 4**K - 2) // 3

def Dsum(n0, K, N):          # exact steps of K digit rules, D(n) = 8n^2-11n+9, N = n_K
    c = Fr(3*n0 + 2, 3)
    X = Fr(N) + Fr(2, 3)
    return Fr(8, 15) * (X*X - c*c) - Fr(65, 9) * (X - c) + Fr(179, 9) * K

# check the closed form against direct summation
for n0, K in ((4, 3), (4, 7), (14, 5)):
    n, s = n0, 0
    for _ in range(K):
        s += 8*n*n - 11*n + 9; n = 4*n + 2
    assert Dsum(n0, K, n) == s and n == N_of(n0, K)
# literal trajectory anchors: S(4,99,2) at step 46783
T2 = 40 + (4*10 + 6) + Dsum(4, 3, 298) + (4*298 + 6)
assert T2 == 46783, T2
K3 = (14 * 4**99 - 5) // 9
assert (14 * 4**99 - 5) % 9 == 0
N2 = N_of(4, 99)
assert K3 == (N2 - 1) // 3
print('K3 =', K3)
print('K3 mod 27 =', K3 % 27)
L4 = mp.log10(4)
K3m = mp.mpf(K3)
log10_K4 = K3m * L4 + mp.log10(mp.mpf(14) / 9)          # K4 = (14*4^K3 - 20)/9
log10_log10_N4 = log10_K4 + mp.log10(L4)                   # log10 N4 = K4 log10 4 + log10(44/3)
print('log10 K4            = %s' % mp.nstr(log10_K4, 15))
print('log10 log10 N4      = %s' % mp.nstr(log10_log10_N4, 15))
print('log10 log10 log10 N4 = %s' % mp.nstr(mp.log10(log10_log10_N4), 15))
# sigma = 2(N4+1)/3 + 5 ~ (2/3) N4 ; steps ~ (8/15) N4^2
print('log10 log10 sigma   = %s' % mp.nstr(log10_log10_N4, 15), '(same to this precision)')
print('log10 log10 steps   = %s' % mp.nstr(log10_log10_N4 + mp.log10(2), 15))
# compare with 2^^6, 2^^7
l2 = mp.log10(2)
x = mp.mpf(2)**65536   # 2^^5
print('2^^6 = 10^10^%s' % mp.nstr(mp.log10(x * l2), 10))
print('2^^7 = 10^10^10^%s' % mp.nstr(mp.log10(x * l2), 10))
