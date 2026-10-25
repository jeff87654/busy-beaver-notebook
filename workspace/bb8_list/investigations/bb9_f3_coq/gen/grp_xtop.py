"""P3 (exhaustion #2 of X; the far-left E0 takes K0 = 0RC):
  XTOPENTRY: Kt(0,0,1^(N+5);1;R+2;3) -> D0f 4 (3N+20) 2 1 (2R) (const 0)   (use site R = 3R'; C04's TOPENTRY: 3N+14, 6R'+2)
  XTOP1:     D0f t (5J+24) 2 1 y (const 0) -> D0f (3+t) (3J+2) (2y+11) 0 (J+6) (const 0)   (sub-step c=4 at P=2)."""
from common import *
from shapes import *
from grp_top import KK, D0raw
XTE_S = KK(3, accr(2, 'R', (0, 1)), tok(1), list(Z) * 5 + [run(Z, N=1)])
XTE_T = D0raw(4, False, [run((1, 1, 1), N=1)] + [1] * 20, [0, 0, 1] * 2, [run((0, 1) * 2, R=1)], [0, 1] * 2)
XT1_S = D0raw(0, True, [run((1,) * 5, J=1)] + [1] * 24, [0, 0, 1] * 2, [run((0, 1), y=1)], [0, 1] * 2)
XT1_T = D0raw(3, True, [run((1, 1, 1), J=1)] + [1] * 2, [0, 0, 1] * 11 + [run((0, 0, 1) * 2, y=1)],
              [0, 1] * 6 + [run((0, 1), J=1)], [0, 1])
ITEMS = [('XTOPENTRY', XTE_S, XTE_T, dict(splits=3, maxstages=400, positive=frozenset(['R'])), ('R',)),
         ('XTOP1', XT1_S, XT1_T, dict(splits=0, maxstages=400), ())]
