"""Phase B split in two (mexp could not do it in one piece: the main loop runs over (101)^(4acc+n-2), two run vars):
 PB1: Kx(1^n ++ [1]; 1; acc; t; e1) -->+ W(X,t) = 111 (01)^7 (101)^X 0 11 (11111100)^t 1001 B> (far-first), X = 4acc+n-2
 PB2: W(X,t) -->+ Kt(1^(X-2) ++ [7]; 1; 2; t)  (frame 11).   (literal: tools/kfit.py; n = k+11, acc = a+5, X = x+12)"""
import os
from common import *
from shapes import *
from grp_ph import A, Zs, tokA, E11, E1
def tl(): return [1, 0, 0, 1] + [run(TB, t=1), 1, 1]
def W(xcells): return ('B', tl() + [0] + xcells + [1, 0] * 7 + [1, 1, 1, BLANK], [BLANK], '>')
PB1_S = ('B', tl() + A + tok(1) + Zs(11) + tok(1) + E1, [BLANK], '>')
PB1_T = W([run((1, 0, 1) * 4, a=1), run((1, 0, 1), k=1)] + [1, 0, 1] * 29)       # X = 4(a+5) + (k+11) - 2 = 4a + k + 29
PB2_S = W([run((1, 0, 1), x=1)] + [1, 0, 1] * 12)
PB2_T = ('B', tl() + accr(2) + tok(1) + list(Z) * 10 + [run(Z, x=1)] + tok(7) + E11, [BLANK], '>')
ITEMS = [('PB1', PB1_S, PB1_T, dict(splits=2, maxstages=3000), ()),
         ('PB2', PB2_S, PB2_T, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
