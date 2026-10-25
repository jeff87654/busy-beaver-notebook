"""Phase B in two pieces (whole-phase mexp fails):
 PBab: Kx(1^n ++ [1]; 1; acc; t; e1) -->+ S2(x,t) = 1010 111 (001)^x (11111001)^t 001 B> (far-first), x = 4acc+n
 PBc : S2(x,t) -->+ Kt(1^(x-4) ++ [7]; 1; 2; t)  (frame 11).   (literal: tools/kfit.py; n = k+11, acc = a+5)"""
import os
from common import *
from shapes import *
from grp_ph import A, Zs, tokA, E11, E1
def tl(): return [1, 0, 0, 1] + [run(TB, t=1), 1, 1]
def S2(xcells): return ('B', [1, 0, 0, run((1, 0, 0, 1, 1, 1, 1, 1), t=1)] + xcells + [1, 1, 1, 0, 1, 0, 1, BLANK], [BLANK], '>')
PBab_S = ('B', tl() + A + tok(1) + Zs(11) + tok(1) + E1, [BLANK], '>')
# the reached syntactic form (Coq's finish_norm cannot rotate (11111001)^t):
# S2n x t = 1001001 (11111001)^t 00 (100)^29 1 (001)^x 110101 (nearest-first), x = k + 4a  (old x = this x + 31)
def S2n(xcells):
    return ('B', [1, 0, 0, 1, 0, 0, 1, run((1, 1, 1, 1, 1, 0, 0, 1), t=1), 0, 0] + [1, 0, 0] * 29 + [1] + xcells
            + [1, 1, 0, 1, 0, 1, BLANK], [BLANK], '>')
PBab_T = S2n([run((0, 0, 1), k=1), run((0, 0, 1) * 4, a=1)])
PBc_S = S2n([run((0, 0, 1), x=1)])
PBc_T = ('B', tl() + accr(2) + tok(1) + list(Z) * 27 + [run(Z, x=1)] + tok(7) + E11, [BLANK], '>')
ITEMS = [('PBab', PBab_S, PBab_T, dict(splits=2, maxstages=3000), ()),
         ('PBc', PBc_S, PBc_T, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
