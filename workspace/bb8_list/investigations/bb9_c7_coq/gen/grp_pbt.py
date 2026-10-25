"""PB with a concrete tail count (symbolic t gets mexp stuck in the tail):  PB2 (t = 2), PB4 (t = 4).
 PBt: Kx(1^n ++ [1]; 1; acc; t; e1) -->+ Kt(1^(K'-1) ++ [7]; 1; 2; t), n = k+11, acc = a+5, K'-1 = 4a+k+27."""
from common import *
from shapes import *
from grp_ph import A, Zs, tokA, E11, E1
def tlc(tc):
    return [1, 0, 0, 1] + list(TB) * tc + [1, 1]
def K(tc, acc, rest): return ('B', tlc(tc) + acc + tok(1) + rest, [BLANK], '>')
ITEMS = [('PB%d' % tc, K(tc, A, Zs(11) + tok(1) + E1), K(tc, accr(2), Zs(27)[:-1] + [run(Z * 4, a=1), run(Z, k=1)] + tok(7) + E11),
          dict(splits=1, maxstages=3000), ()) for tc in (2, 4)]
