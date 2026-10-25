"""Group 'top': exhaustion #2 = TOPENTRY + TOP1, then generic cascade.
  TOPENTRY: Kt(0,0,1^n;1;3R+2;3) -> D0('',1,6R+2,2,3n-1,4),  n = N+5.
  TOP1:     D0('',1,y,2,5j+5,t) -> D0('',0,j+3,2y+7,3j-7,t+3),  j = J+5.
  D0(l,s,y,P,L,t) = l 1 (10)^(s+1) 1 (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001 B>  (here l = blank)."""
from common import *
from shapes import *
def KK(tcount, acc, atok, mid, tvar=False):
    tail = [1, 0, 0, 1] + list(TB) * tcount + ([run(TB, t=1)] if tvar else []) + [1, 1]
    return ('B', tail + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')
def D0raw(tcon, tvar, Lcells, Pcells, ycells, scells):
    """nearest-first: 1001 TB^t 11 1^L (001)^P 110 (01)^y 1 (01)^(s+1) 1 blank"""
    left = [1, 0, 0, 1] + list(TB) * tcon + ([run(TB, t=1)] if tvar else []) + [1, 1] + Lcells + Pcells
    left += [1, 1, 0] + ycells + [1] + scells + [1, BLANK]
    return ('B', left, [BLANK], '>')
TOPENTRY_S = KK(3, accr(2, 'R', (0, 1) * 3), tok(1), list(Z) * 5 + [run(Z, N=1)])
TOPENTRY_T = D0raw(4, False, [run((1, 1, 1), N=1)] + [1] * 14, [0, 0, 1] * 2,
                   [0, 1] * 2 + [run((0, 1) * 6, R=1)], [0, 1] * 2)
TOP1_S = D0raw(0, True, [run((1,) * 5, J=1)] + [1] * 30, [0, 0, 1] * 2, [run((0, 1), y=1)], [0, 1] * 2)
TOP1_T = D0raw(3, True, [run((1, 1, 1), J=1)] + [1] * 8, [0, 0, 1] * 7 + [run((0, 0, 1) * 2, y=1)],
               [0, 1] * 8 + [run((0, 1), J=1)], [0, 1])
ITEMS = [('TOPENTRY', TOPENTRY_S, TOPENTRY_T, dict(splits=0, maxstages=400), ()),
         ('TOP1', TOP1_S, TOP1_T, dict(splits=0, maxstages=400), ())]
