"""Orbit of the main machine through the family, exact where feasible (python sizes.py)."""
from math import log10
def R1iter(a, b):  # b after a applications of R1 (b -> 4b+4)
    # b_a = 4^a (b + 4/3) - 4/3, exact integer form
    return (4 ** a * (3 * b + 4) - 4) // 3
print('K(2;0;8) -> R2 -> K(1;35;1)')
b35 = R1iter(35, 1)
print('K(1;0;b35), b35 =', b35)
a0 = 4 * b35 + 3
print('R2 -> K(;a0;1), a0 = 4*b35+3 =', a0)
# b after a0 R1 steps: (4^a0 * 7 - 4)/3 ; log10
lg = a0 * log10(4) + log10(7 / 3)
print('R1^a0 -> K(;0;B), log10(B) = %.6e' % lg)
print('R4 -> K(2,1^(4B);1;1): number of digits 4B+1, log10 = %.6e' % (lg + log10(4)))
# Quick_Sim cross-check (1500 loops): a-run 2X+2 with X = 5509427563347919408983
X = 5509427563347919408983
print('Quick_Sim 1500 loops: a =', 2 * X + 2, ' R1 steps done =', a0 - (2 * X + 2))
