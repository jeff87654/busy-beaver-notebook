"""(start = M1n x t, PA1's target; x = c - 26)
   PA2 / PC2 (C7 / X'): from M1 = 111 00 111 (001)^c (11111001)^t 001 B> (far-first; PA1's target):
   PA2 (c = 5j+21 = 1 mod 5): -->+ Kx(1^(K-2) ++ [K+5; 1]; 1; 2; t+2; frame 1),  K = (3c-8)/5 = 3j+11
   PC2 (c = 5j+23 = 3 mod 5): -->+ Kx(1^(K-1) ++ [K-12]; 1; 2; t+2; 00 D7 D1 frame 11), K = (3c+26)/5 = 3j+19."""
from common import *
from shapes import *
TBR = (1, 0, 0, 1, 1, 1, 1, 1)
def M1(x0):
    """PA1's target M1n x t with x = 5j + x0"""
    return ('B', [1, 0, 0, 1, 0, 0, 1, run((1, 1, 1, 1, 1, 0, 0, 1), t=1), 0, 0] + [1, 0, 0] * 24 + [1] + [0, 0, 1] * x0
            + [run((0, 0, 1) * 5, j=1), 1, 1, 0, 0, 1, 1, 1, BLANK], [BLANK], '>')
def tail2():
    return [1, 0, 0, 1] + list(TB) * 2 + [run(TB, t=1), 1, 1]
PA2_T = ('B', tail2() + accr(2) + tok(1) + list(Z) * 12 + [run(Z * 3, j=1)] + [1] + [0, 1] * 19 + [run((0, 1) * 3, j=1)]
         + tok(1) + [1, BLANK], [BLANK], '>')
PC2_T = ('B', tail2() + accr(2) + tok(1) + list(Z) * 21 + [run(Z * 3, j=1)] + [1] + [0, 1] * 10 + [run((0, 1) * 3, j=1)]
         + [0, 0] + tok(7) + tok(1) + [1, 1, BLANK], [BLANK], '>')
ITEMS = [('PA2', M1(0), PA2_T, dict(splits=2, maxstages=400), ()),
         ('PC2', M1(2), PC2_T, dict(splits=2, maxstages=400), ())]
