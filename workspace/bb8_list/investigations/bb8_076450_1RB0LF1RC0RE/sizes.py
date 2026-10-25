"""Closed forms, exact small values and magnitudes for 1RB0LF_1RC0RE_1LD1LC_1LA0LD_1LB1RA_1RG1LG_0LH0RD_---1RF.
Also checks the literal step counts of check_rules_main.json against the linear step formulas.

S(n,k,j) = 0^inf A>0 1^n (001)^k 000 1^j 0^inf.  From S(n0,K,j): N = ((3 n0 + 2) 4^K - 2)/3.
"""
import json
from fractions import Fraction as Fr
from math import log10

# ---- literal step counts of the tape rules (check_rules.py, empty context) are exactly linear
res = json.load(open('check_rules_main.json'))['results']
forms = {'O': lambda p: 12 * p + 9, 'E': lambda p: 12 * p, 'R2': lambda q: 40 * q + 28,
         'R4': lambda q: 40 * q + 25, 'R0': lambda q: 40 * q - 2}
for name, f in forms.items():
    st = {int(k): v for k, v in res[name]['steps'].items()}
    assert all(v == f(k) for k, v in st.items()), name
    print('%-2s steps match formula for %d parameter values' % (name, len(st)))
# in terms of n:  O: 6n+3 (n = 2p+1 odd);  E: 6n (n = 2p);  R2: (20n+44)/3;  R4: (20n-5)/3;  R0 (to the halt): (20n-6)/3


def D(n):          # digit rule S(n,k+1,j) -> S(4n+2,k,j): E then 2p-1 rules O
    p = n // 2
    return 12 * p + sum(12 * m + 9 for m in range(0, 2 * (2 * p - 1), 2))


for n in range(2, 200, 2):
    assert D(n) == 12 * n * n - 21 * n + 15
print('digit rule cost D(n) = 12n^2 - 21n + 15 (checked n = 2..198)')


def dsum_closed(n0, K):
    N = ((3 * n0 + 2) * 4 ** K - 2) // 3
    c = Fr(2, 3)
    return Fr(4, 5) * ((N + c) ** 2 - (n0 + c) ** 2) - Fr(37, 3) * (N - n0) + Fr(103, 3) * K, N


for n0 in (8, 10):
    for K in range(0, 12):
        n, s = n0, 0
        for _ in range(K):
            s += D(n); n = 4 * n + 2
        ds, N = dsum_closed(n0, K)
        assert ds == s and N == n
print('Dsum closed form checked')

# ---- trajectory
N0 = 10                                   # S(10,0,0) at step 48
assert N0 % 6 == 4; K1 = (N0 - 4) // 3    # reset 0 (R4 + two O): S(10,2,1)
N1 = (32 * 4 ** K1 - 2) // 3; assert N1 == 170 and N1 % 6 == 2
K2 = (N1 - 5) // 3; assert K2 == 55       # reset 1 (R2): S(8,55,2)
N2 = (26 * 4 ** K2 - 2) // 3; assert (26 * 4 ** K2 - 2) % 3 == 0
print('N2 =', N2, ' N2 mod 6 =', N2 % 6, ' (N2/2 mod 9 = %d)' % (N2 // 2 % 9))
assert N2 % 6 == 4
K3 = (N2 - 4) // 3                        # reset 2 (R4 + two O): S(10,K3,3)
print('K3 =', K3, ' (%d digits), K3 mod 3 = %d' % (len(str(K3)), K3 % 3))
# N3 = (32*4^K3 - 2)/3, N3/2 = p with p = 5 + K3 (mod 3)
assert (5 + K3) % 3 == 0
MOD = 54
N3m = ((32 * pow(4, K3, 3 * MOD) - 2) % (3 * MOD)) // 3
print('N3 mod 6 =', N3m % 6, '-> R0: HALT at reset 3 with j = 3')
assert N3m % 6 == 0

# ---- score
L4 = log10(4)
log10_N3 = log10(32 / 3) + K3 * L4
log10_sigma = log10(32 / 9) + K3 * L4       # sigma = N3/3 + 5 = (32*4^K3 + 43)/9
print('sigma = (32*4^K3 + 43)/9;  log10 sigma = %.6e' % log10_sigma)
print('  log10 log10 sigma = %.6f ; log10 log10 log10 sigma = %.6f' % (log10(log10_sigma), log10(log10(log10_sigma))))
print('  2^^5 = 10^%.2f < sigma < 2^^6 = 10^10^%.2f' % (65536 * log10(2), 65536 * log10(2) + log10(log10(2))))
# steps
pre = 48 + ((20 * 10 - 5) // 3 + 42) + dsum_closed(10, 2)[0] + (20 * 170 + 44) // 3
assert pre == 22609
print('S(8,55,2) at step', pre)
# T = 22609 + Dsum(8,55) + (20 N2 - 5)/3 + 42 + Dsum(10,K3) + (20 N3 - 6)/3  ~  (4/5) N3^2
log10_T = log10(4 / 5) + 2 * log10_N3
print('steps T ~ (4/5) N3^2 ~ (4/5)(32/3)^2 16^K3;  log10 T = %.6e ; log10 log10 T = %.6f' % (log10_T, log10(log10_T)))
S1 = pre + dsum_closed(8, 55)[0] + (20 * N2 - 5) // 3 + 42
print('S(10,K3,3) reached at step', S1, '(%d digits)' % len(str(S1)))
