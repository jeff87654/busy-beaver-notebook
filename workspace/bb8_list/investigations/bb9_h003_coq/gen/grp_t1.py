"""T1 (h003 / X3), K = 1 mod 5, in two pieces (whole-phase mexp: stuck without loop):
 T1a: Kt(1^K;1;A;t) -->+ Kx(1^K' ++ [3];1;2;t+3;e1)       K = 5k+11, A = a+5 (= 3R+2), K' = 4a + 9k + 39 (= 12R + (9K+36)/5)
 T1b: Kx(1^(n+1) ++ [3];1;2;t;e1) -->+ Kt(1^n ++ [7];1;2;t)  (one borrow, n = k+5)
 Literal: tools/x3sim.py (K = 11, 16; R = 6, 16)."""
import os
from common import *
from shapes import *
def tl(tc=0): return [1, 0, 0, 1] + list(TB) * tc + [run(TB, t=1), 1, 1]
START = ('B', tl() + accr(5, 'a', (0, 1)) + tok(1) + list(Z) * 11 + [run(Z * 5, k=1)] + [1, 1, BLANK], [BLANK], '>')
T1a_T = ('B', tl(3) + accr(2) + tok(1) + list(Z) * 39 + [run(Z * 4, a=1), run(Z * 9, k=1)] + tok(3) + [1, BLANK], [BLANK], '>')
T1b_S = ('B', tl() + accr(2) + tok(1) + list(Z) * 6 + [run(Z, k=1)] + tok(3) + [1, BLANK], [BLANK], '>')
T1b_T = ('B', tl() + accr(2) + tok(1) + list(Z) * 5 + [run(Z, k=1)] + tok(7) + [1, 1, BLANK], [BLANK], '>')
# T1a in two pieces (T1a whole: stuck without loop): the common moment M1 (literal, tools/trace1.py, all K):
# M1n x t = 1001001 (11111001)^t 1^x 001001110 (01)^(2a+9) 101011 B>  (nearest-first), x = 3K+6 = 15k+39
def M1n(xc): return ('B', [1, 0, 0, 1, 0, 0, 1, run((1, 1, 1, 1, 1, 0, 0, 1), t=1)] + xc + [0, 0, 1, 0, 0, 1, 1, 1, 0]
                     + [0, 1] * 9 + [run((0, 1) * 2, a=1)] + [1, 0, 1, 0, 1, 1, BLANK], [BLANK], '>')
M1_k = M1n([run((1,) * 15, k=1)] + [1] * 39)
ITEMS = [('T1a', START, T1a_T, dict(splits=2, maxstages=3000), ()),
         ('T1a1', START, M1_k, dict(splits=2, maxstages=3000), ()),
         ('T1a2', M1_k, T1a_T, dict(splits=2, maxstages=3000), ()),
         ('T1b', T1b_S, T1b_T, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
# T1a2 in two pieces (T1a2 whole: stuck in the far-left transfer loop over the merged token (10)^(2a+3k+18)):
# Y x m t = 1 A> 1 (10)^x 0 (101)^m (10011100)^(t+1) 100101  (far-first; literal tools/x3sim.py: x = 2a+3k+18, m = 3k+10)
TBR = (1, 0, 0, 1, 1, 1, 0, 0)
def Y(xc, mc): return ('A', [1, BLANK], [1] + xc + [0] + mc + list(TBR) + [run(TBR, t=1)] + [1, 0, 0, 1, 0, 1, BLANK], '>')
Y_ak = Y([1, 0] * 18 + [run((1, 0) * 2, a=1), run((1, 0) * 3, k=1)], [1, 0, 1] * 10 + [run((1, 0, 1) * 3, k=1)])
Y_xk = Y([run((1, 0), x=1)], [1, 0, 1] * 10 + [run((1, 0, 1) * 3, k=1)])
T1a_Tx = ('B', tl(3) + accr(2) + tok(1) + list(Z) * 3 + [run(Z * 2, x=1), run(Z * 3, k=1)] + tok(3) + [1, BLANK], [BLANK], '>')
ITEMS += [('T1a2a', M1_k, Y_ak, dict(splits=2, maxstages=3000), ()),
          ('T1a2b', Y_xk, T1a_Tx, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
# T1a2b by Coq induction (T1a2b in mexp: timeout 1500 s).  Y n m t (above), literal tools/ysim.py:
#  YR : Y (n+2) m -->+ Y (n+1) (m+2)        YE : Y 1 (m+6) -->+ Kx(1^(m+1) ++ [3];1;2;t+3;e1)
YR_S = Y([1, 0, 1, 0] + [run((1, 0), n=1)], [run((1, 0, 1), m=1)])
YR_T = Y([1, 0] + [run((1, 0), n=1)], [1, 0, 1] * 2 + [run((1, 0, 1), m=1)])
YE_S = Y([1, 0], [1, 0, 1] * 6 + [run((1, 0, 1), m=1)])
YE_T = ('B', tl(3) + accr(2) + tok(1) + list(Z) * 1 + [run(Z, m=1)] + tok(3) + [1, BLANK], [BLANK], '>')
ITEMS += [('YR', YR_S, YR_T, dict(splits=2, maxstages=3000), ()),
          ('YE', YE_S, YE_T, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
