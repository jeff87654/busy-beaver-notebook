"""The r = 2 branch, first part split in two (whole R2A got stuck in mexp):
 R2A1: D0f (t+1) (15u+17) (p+2) s y l -->+ W1 = l 1 (10)^s 101 (10)^y 0 111 (001)^(p+1) 0 11111 (00111)^(3u+4) (11100111)^t 111 001001 B>
 R2A2: W1 with p+1 = 4u+4+p' -->+ M2 (grp_r2.M2, with p' and tail t+1).   (W1 formula verified on 9 parameter sets.)"""
import os
from common import *
from shapes import *
from grp_sub import d0, Y, S, L
# the real run has s = 2 (after sub3) and y large: fix s = 2, y = y'+5 (symbolic s gets mexp stuck: s = 0 differs)
SC = [0, 1, 0, 1]
YC = [run((0, 1), y=1)] + [0, 1] * 5
from grp_r2 import M2, uvar
TBM = (1, 1, 1, 0, 0, 1, 1, 1)
def W1(pcells, tx=0):
    return ('B', [1, 0, 0, 1, 0, 0, 1, 1, 1] + list(TBM) * tx + [run(TBM, t=1), run((1, 1, 1, 0, 0) * 3, u=1)] + [1, 1, 1, 0, 0] * 4 + [1] * 5 + [0]
            + pcells + [1, 1, 1, 0, *YC, 1, 0, 1, *SC, 1, V('l')], [BLANK], '>')
R2A1_S = d0(1, [run((1,) * 15, u=1)] + [1] * 17, [run((0, 0, 1), p=1)] + [0, 0, 1] * 2, YC, SC, L)
R2A1_T = W1([run((1, 0, 0), p=1), 1, 0, 0])
# real run: p and t large; p >= 3, t >= 1 here (p = 0 / t = 0 behave differently and get mexp stuck)
R2A2_S = W1([run((1, 0, 0) * 4, u=1)] + [1, 0, 0] * 7 + [run((1, 0, 0), p=1)], tx=1)
_m2 = M2(uvar, [1, 0, 0] * 3 + [run((1, 0, 0), p=1)])
R2A2_T = (_m2[0], _m2[1][:9] + list(TBM) * 2 + _m2[1][9:], _m2[2], _m2[3])
ITEMS = [('R2A1', R2A1_S, R2A1_T, dict(splits=2, maxstages=3000), ()),
         ('R2A2', R2A2_S, R2A2_T, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
