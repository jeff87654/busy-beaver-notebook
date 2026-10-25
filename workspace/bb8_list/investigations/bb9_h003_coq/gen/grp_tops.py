"""h003 / X3 top-level phases (literal: tools/x3sim.py walk / d0walk).  A = a+5 (= 3R+2), so 6R+c = 2a+c+6.
 P3 : K = 5k+13: Kt(1^K;1;A;t) -->+ CL Kx(1^(Kb-1) ++ [Kb+8; 2a+7; 1; 0];1;2;t+3; blank), Kb = (3K-14)/5 = 3k+5
 P4 : K = 5k+14: Kt(1^K;1;A;t) -->+ CL Kx(1^(Ka-1) ++ [Ka+7];1;2;t+3; 00 D2 D(2a+11) D1 D0 blank), Ka = 3k+3
 P4b: Ka = k+3, B = b+5 (= 3R_b+2): Kx(1^Ka;1;B;t; 00 D2 D(2a+11) D1 D0 blank) -->+
        CL Kx(1^(Ka-2) ++ [2b+16; 2a+10; 1; 0];1;2;t; blank)
 TXa: K = 5k+15: Kt(1^K;1;A;t) -->+ D0f (t+1) (3K-1) 2 1 (2a+9) blank"""
import os
from common import *
from shapes import *
from grp_sub import d0
def tl(tc=0): return [1, 0, 0, 1] + list(TB) * tc + [run(TB, t=1), 1, 1]
def tokv(c, var, coef): return [1] + [0, 1] * c + [run((0, 1) * coef, **{var: 1})]
A = accr(5, 'a', (0, 1)); Bb = accr(5, 'b', (0, 1))
def Kst(k0): return ('B', tl() + A + tok(1) + list(Z) * k0 + [run(Z * 5, k=1)] + [1, 1, BLANK], [BLANK], '>')
FAR4 = [0, 0] + tok(2) + tokv(11, 'a', 2) + tok(1) + tok(0)
P3_T = ('B', tl(3) + accr(2) + tok(1) + list(Z) * 4 + [run(Z * 3, k=1)] + tokv(13, 'k', 3) + tokv(7, 'a', 2) + tok(1) + tok(0) + [BLANK], [BLANK], '>')
P4_T = ('B', tl(3) + accr(2) + tok(1) + list(Z) * 2 + [run(Z * 3, k=1)] + tokv(10, 'k', 3) + FAR4 + [BLANK], [BLANK], '>')
P4b_S = ('B', tl() + Bb + tok(1) + list(Z) * 3 + [run(Z, k=1)] + FAR4 + [BLANK], [BLANK], '>')
P4b_T = ('B', tl() + accr(2) + tok(1) + list(Z) * 1 + [run(Z, k=1)] + tokv(16, 'b', 2) + tokv(10, 'a', 2) + tok(1) + tok(0) + [BLANK], [BLANK], '>')
TXa_T = d0(1, [run((1,) * 15, k=1)] + [1] * 44, [0, 0, 1] * 2, [0, 1] * 9 + [run((0, 1) * 2, a=1)], [0, 1], [BLANK])
ITEMS = [('P3', Kst(13), P3_T, dict(splits=2, maxstages=3000), ()),
         ('P4', Kst(14), P4_T, dict(splits=2, maxstages=3000), ()),
         ('P4b', P4b_S, P4b_T, dict(splits=2, maxstages=3000), ()),
         ('TXa', Kst(15), TXa_T, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
