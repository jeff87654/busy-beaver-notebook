"""XTOP1 on X3 (= bb9_f3_coq gen/grp_xtop.py's XTOP1; C04's own TOP1 is for D0f L-field 5J+30, h003's exit needs 5J+24):
  XTOP1: D0f t (5J+24) 2 1 y (const 0) -> D0f (3+t) (3J+2) (2y+11) 0 (J+6) (const 0)   (sub-step at P=2).
  Literal (tools/x3sim.py d0walk): K = 15..45, R = 6, 16, t = 0, 3, 6."""
import os
from common import *
from shapes import *
from grp_top import KK, D0raw
XT1_S = D0raw(0, True, [run((1,) * 5, J=1)] + [1] * 24, [0, 0, 1] * 2, [run((0, 1), y=1)], [0, 1] * 2)
XT1_T = D0raw(3, True, [run((1, 1, 1), J=1)] + [1] * 2, [0, 0, 1] * 11 + [run((0, 0, 1) * 2, y=1)],
              [0, 1] * 6 + [run((0, 1), J=1)], [0, 1])
ITEMS = [('XTOP1', XT1_S, XT1_T, dict(splits=0, maxstages=400), ())]
