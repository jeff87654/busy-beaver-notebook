"""Phase A of C7 (X'): Kt(1^n;1;3R+2;t) (frame 11) -->+ [frame 1 | 1, K+5, 1^(K-1) ; m=1, r=2], t+2,
   n = 5k+1, R = 5q+1 (acc 3R+2 = 15q+5), K = 27q+3k+8 (= (27R+3n+10)/5).  Test instance: k, q, t free."""
from common import *
from shapes import *
def tail(tc, tvar):
    return [1, 0, 0, 1] + list(TB) * tc + ([run(TB, t=1)] if tvar else []) + [1, 1]
START = ('B', tail(0, True) + accr(5, 'q', (0, 1) * 15) + tok(1) + list(Z) + [run(Z * 5, k=1)] + [1, 1, BLANK], [BLANK], '>')
TARGET = ('B', tail(2, True) + accr(2) + tok(1) + list(Z) * 6 + [run(Z * 27, q=1), run(Z * 3, k=1)]
          + [1] + [0, 1] * 13 + [run((0, 1) * 27, q=1), run((0, 1) * 3, k=1)] + tok(1) + [1, BLANK], [BLANK], '>')
ITEMS = [('PA', START, TARGET, dict(splits=2, maxstages=400), ())]
