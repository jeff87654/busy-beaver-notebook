"""PA1 (C7 / X'): Kt(1^n;1;A;t) (frame 11) -->+ M1 = 111 00 111 (001)^c (11111001)^t 001 B>  (far-first),
   A = a+5 (= 3R+2), n = k+11, c = 3a + k + 26 (= 9R + n + 6).  Literal: tools/pascan.py (R = 6, 11; n = 11, 16;
   t = 0, 2, 4).  The far-left transfer loop (C7's H0 with blank left, I0 = 1LC) is inside."""
from common import *
from shapes import *
def tail(tc, tvar):
    return [1, 0, 0, 1] + list(TB) * tc + ([run(TB, t=1)] if tvar else []) + [1, 1]
START = ('B', tail(0, True) + accr(5, 'a', (0, 1)) + tok(1) + list(Z) * 11 + [run(Z, k=1)] + [1, 1, BLANK], [BLANK], '>')
# target = the form the run actually reaches (Coq's finish_norm cannot rotate (11111001)^t past fixed cells):
# M1n x t = 1001001 (11111001)^t 00 (100)^24 1 (001)^x 1100111  (nearest-first), x = k + 3a  (= c - 26 of the old M1)
TARGET = ('B', [1, 0, 0, 1, 0, 0, 1, run((1, 1, 1, 1, 1, 0, 0, 1), t=1), 0, 0] + [1, 0, 0] * 24 + [1, run((0, 0, 1), k=1), run((0, 0, 1) * 3, a=1)]
          + [1, 1, 0, 0, 1, 1, 1, BLANK], [BLANK], '>')
ITEMS = [('PA1', START, TARGET, dict(splits=2, maxstages=400), ())]
