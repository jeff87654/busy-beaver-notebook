"""Sizes along the (never-ending) trajectory of 1RB0RD_1RC0RE_1LD1LC_1LA0LD_1LB1RF_---1LG_0RB1RH_0LB1RG.
  Mc a (b+3) t -> Mc (6a+6) b t;  Mc a 0 T1 -> Mc 4 (6a+7) T2;  Mc a 1 T2 -> Mc 4 (6a+3) T1.
  f^k(4) = (26*6^k - 6)/5.  Blank tape -> Mc 4 1 T2 (step 82) -> Mc 4 27 T1 (step 415)."""
from math import log10
def f_iter(k, a=4):
    return (26 * 6**k - 6) // 5 if a == 4 else None
# exact check of the closed form against iteration for small k
a = 4
for k in range(12):
    assert a == (26 * 6**k - 6) // 5 and (26 * 6**k - 6) % 5 == 0
    a = 6 * a + 6
a1 = f_iter(9)
print('phase 1: Mc 4 27 T1 -> Mc a1 0 T1, a1 = f^9(4) =', a1)
b2 = 6 * a1 + 7; k2 = (b2 - 1) // 3
print('phase 2: Mc 4 %d T2 (b = 3*%d + 1), %d digits' % (b2, k2, k2))
L6 = log10(6); L52 = log10(26 / 5)
log_a2 = k2 * L6 + L52
print('  a2 = f^k2(4) = (26*6^k2 - 6)/5, log10 a2 = %.6e' % log_a2)
print('  a2 ~ 10^(%.4e)' % log_a2)
e3 = log10(2 * L6) + log_a2          # log10 log10 a3
print('phase 3: Mc 4 (6 a2 + 3) T1, k3 = 2 a2 + 1 digits, a3 = f^k3(4): log10 a3 ~ 2 a2 log10 6, so a3 ~ 10^10^(%.4e)' % e3)
print('phase 4: Mc 4 (6 a3 + 7) T2, k4 = 2 a3 + 2 digits, a4 = f^k4(4) ~ 10^10^10^(%.4e)' % e3)
print('Each later phase adds one exponential level (a_{j+1} ~ 6^(2 a_j)): tetration growth, never halting.')
# pipeline position: Quick_Sim was in phase 2 (9,297 / 16,970 / 31,257 digits)
for d in (9297, 16970, 31257):
    print('  %6d digits = about %d of the %d digit rules of phase 2' % (d, d / L6, k2))
