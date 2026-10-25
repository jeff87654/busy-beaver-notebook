"""ENTRY1 (C7 / X'): the cascade entry plus its first sub-step (L1 = 3n-4 = 1 mod 5):
   Kx(1^n; 1; acc; t; blank) -->+ D0f (t+3) (9m-7) (4 acc - 4) 0 (3m+3) blank,   n = 5m, m = k+10, acc = a+5.
   (literal: n = 100 -> D0 t+3, L 173, P 196 (R = 16), y 63, far '0 1' = s 0, l blank)."""
import os
from common import *
from shapes import *
from grp_sub import d0
def tl(): return [1, 0, 0, 1] + [run(TB, t=1), 1, 1]
START = ('B', tl() + accr(5, 'a', (0, 1)) + tok(1) + list(Z) * 50 + [run(Z * 5, k=1)] + [BLANK], [BLANK], '>')
TARGET = d0(3, [run((1,) * 9, k=1)] + [1] * 83, [run((0, 0, 1) * 4, a=1)] + [0, 0, 1] * 16,
            [run((0, 1) * 3, k=1)] + [0, 1] * 33, [], [BLANK])
ITEMS = [('ENTRY1', START, TARGET, dict(splits=2, maxstages=3000), ())]
