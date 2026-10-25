"""Closed forms and magnitudes for 1RB1RH_0LC0LF_1LE1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---.
k_{i+1} = (87*9^{k_i} + 1)/16 (odd resets), k0 = 1, k1 = 49; k5 even -> halt.
N5 = F(k5,2) = (29*9^k5 - 13)/8, m5 = 3*N5 + 4, sigma = (9*N5 + 24)/2 = (261*9^k5 + 75)/16.
Steps ~ 13.5*N5^2 ~ (2/3) sigma^2 (last phase dominates)."""
from math import log10
l9 = log10(9)
k1 = 49
assert (87 * 9**k1 + 1) % 16 == 0
k2 = (87 * 9**k1 + 1) // 16
print('k2 =', k2)
print('log10 k2 = %.9f' % log10(k2))
Lk3 = k2 * l9 + log10(87 / 16)              # log10 k3 (exact up to float rounding of l9*k2)
print('log10 k3 = %.9e' % Lk3)
# log10 k4 = k3*l9 + log10(87/16)  =>  log10 log10 k4 = log10 k3 + log10(l9) + tiny
LLk4 = Lk3 + log10(l9)
LLLk5 = LLk4 + log10(l9)
# log10 sigma = k5*l9 + log10(261/16)  =>  log10^2 sigma = log10 k5 + log10(l9); log10^4 sigma = log10^3 k5 + ...
L4s = LLLk5 + log10(l9)
print('log10^2 k4 = %.9e, log10^3 k5 = %.9e, log10^4 sigma = %.9e' % (LLk4, LLLk5, L4s))
print('sigma = 10^10^10^10^(%.6e) = 10^10^10^10^10^%.6f' % (L4s, log10(L4s)))
# 2^^5 = 10^19728.3, 2^^6 = 10^10^19727.78 = 10^10^10^4.2951, each further 2^ adds one 10^ (up to rounding)
t = log10(19727.78)
print('2^^8 ~ 10^10^10^10^10^%.4f < sigma < 2^^9 ~ 10^10^10^10^10^%.1f ; 10^^6 = 10^10^10^10^10^10 < sigma < 10^^7' % (t, 19727.78))
