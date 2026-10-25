"""The r = 2 branch of C7's cascade (X'), split in two (literal fits: tools/bfit.py and the halting traces):
 R2A: D0f t (15u+17) (4u+5+p) s y l -->+ M2   (u rounds; each eats 15 L-cells and 4 parked blocks, deposits a D4)
      M2 far-first = l 1 (10)^s 1 (10)^y (1(10)^4)^u 101 (10)^4 0 111 (001)^p 11111 (001)^(6u+6) (11100111)^t 111 001001 B>
 R2H: M2 with u = 5j+2 and p = p'+1 -->* the halting configuration (X' in J reading 1; C7's H1):
      l 1 (10)^s 1 (10)^y (1(10)^4)^(u+1) (10)^3 (110)^p' J> 11111 (00111)^(18j+11) (00100111)^t 00100101."""
import os
from common import *
from shapes import *
from grp_sub import d0, Y, S, L
# the real run has s = 2 (after sub3) and y large: fix s = 2, y = y'+5 (symbolic s gets mexp stuck: s = 0 differs)
SC = [0, 1, 0, 1]
YC = [run((0, 1), y=1)] + [0, 1] * 5
def M2(urun, prun):
    return ('B', [1, 0, 0, 1, 0, 0, 1, 1, 1, run((1, 1, 1, 0, 0, 1, 1, 1), t=1)] + urun((1, 0, 0) * 6) + [1, 0, 0] * 6 + [1] * 5
            + prun + [1, 1, 1, 0] + [0, 1] * 4 + [1, 0, 1] + urun((0, 1, 0, 1, 0, 1, 0, 1, 1)) + [*YC, 1, *SC, 1, V('l')],
            [BLANK], '>')
def uvar(blk): return [run(blk, u=1)]
def u52(blk): return [run(blk * 5, j=1)] + list(blk) * 2
R2A_S = d0(0, [run((1,) * 15, u=1)] + [1] * 17, [run((0, 0, 1) * 4, u=1)] + [0, 0, 1] * 5 + [run((0, 0, 1), p=1)], YC, SC, L)
R2A_T = M2(uvar, [run((1, 0, 0), p=1)])
R2H_S = M2(u52, [1, 0, 0, run((1, 0, 0), p=1)])
D4 = (0, 1, 0, 1, 0, 1, 0, 1, 1)
R2H_T = ('J', [run((0, 1, 1), p=1)] + [0, 1] * 3 + [run(D4 * 5, j=1)] + list(D4) * 3 + [*YC, 1, *SC, 1, V('l')],
         [1] * 5 + [run((0, 0, 1, 1, 1) * 18, j=1)] + [0, 0, 1, 1, 1] * 11 + [run((0, 0, 1, 0, 0, 1, 1, 1), t=1)] + [0, 0, 1, 0, 0, 1, 1, 1] + [0, 0, 1, 0, 0, 1, 0, 1, BLANK], '>')
ITEMS = [('R2A', R2A_S, R2A_T, dict(splits=2, maxstages=3000), ()),
         ('R2H', R2H_S, R2H_T, dict(splits=2, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
