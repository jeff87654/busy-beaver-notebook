"""The r = 2 branch as PRE + ROUND (one round, composed by induction in Coq) + VH (the halt):
 V(d,A,b,c,t) = X' in J reading 0 (C7's H0 event), far-first left l 1 (10)^s 1 (10)^y (1(10)^4)^d 101 (10)^4 0 111 (001)^A,
                right 0 1111 0 (01)^b 00 (101)^c (10011100)^t 100101      (s = 2, y = y'+5 as in the real run)
 PRE  : W1 (from R2A1; (001)^(A+5), tail (11100111)^t) -->+ V(0, A, 3u+1, 3u+6, t+1)
 ROUND: V(d, A+4, b+4, c, t+1) -->+ V(d+1, A, b+1, c+3, t+1)
 VH   : V(d, A, 1, 30jj+18, t+1)  (c = 6u+6, u = 5jj+2) -->* halt: J reading 1, left (011)^A (01)^3 ((01)^4 1)^(d+1) (01)^y 1 (01)^s 1 l,
        right 11111 (00111)^(18jj+11) (00100111)^(t+2) 00100101.   (u rounds take b = 3u+1 to 1 and c = 3u+6 to 6u+6.)"""
import os
from common import *
from shapes import *
from grp_sub import d0, L
from grp_r2s import W1, TBM, SC, YC
D4 = (0, 1, 0, 1, 0, 1, 0, 1, 1)
TBV = (1, 0, 0, 1, 1, 1, 0, 0)
def V(dcells, Acells, bcells, ccells, tcells, q='J'):
    left = Acells + [1, 1, 1, 0] + [0, 1] * 4 + [1, 0, 1] + dcells + YC + [1] + SC + [1, V_('l')]
    right = [0, 1, 1, 1, 1, 0] + bcells + [0, 0] + ccells + tcells + [1, 0, 0, 1, 0, 1, BLANK]
    return (q, left, right, '>')
V_ = globals()['V'] if False else None
from planner8 import V as V_
TT = [run(TBV, t=1)] + list(TBV)
PRE_S = W1([run((1, 0, 0), A=1)] + [1, 0, 0] * 5)
PRE_T = V([], [run((1, 0, 0), A=1)], [run((0, 1) * 3, u=1), 0, 1], [run((1, 0, 1) * 3, u=1)] + [1, 0, 1] * 6, TT)
RND_S = V([run(D4, d=1)], [run((1, 0, 0), A=1)] + [1, 0, 0] * 4, [run((0, 1), b=1)] + [0, 1] * 4, [run((1, 0, 1), c=1)], TT)
RND_T = V(list(D4) + [run(D4, d=1)], [run((1, 0, 0), A=1)], [run((0, 1), b=1)] + [0, 1], [run((1, 0, 1), c=1)] + [1, 0, 1] * 3, TT)
VH_S = V([run(D4, d=1)], [run((1, 0, 0), A=1)], [0, 1], [run((1, 0, 1) * 30, jj=1)] + [1, 0, 1] * 18, TT)
VH_T = ('J', [run((0, 1, 1), A=1)] + [0, 1] * 3 + list(D4) + [run(D4, d=1)] + YC + [1] + SC + [1, V_('l')],
        [1] * 5 + [run((0, 0, 1, 1, 1) * 18, jj=1)] + [0, 0, 1, 1, 1] * 11 + [run((0, 0, 1, 0, 0, 1, 1, 1), t=1)]
        + [0, 0, 1, 0, 0, 1, 1, 1] * 2 + [0, 0, 1, 0, 0, 1, 0, 1, BLANK], '>')
ITEMS = [('PRE', PRE_S, PRE_T, dict(splits=1, maxstages=3000), ()),
         ('ROUND', RND_S, RND_T, dict(splits=1, maxstages=3000), ()),
         ('VH', VH_S, VH_T, dict(splits=1, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
# fallback split of VH at the B> moment after the last round (M2-like):
#  M2p(d,A,c,t) far-first = l 1 (10)^2 1 (10)^(y+5) (1(10)^4)^d 101 (10)^4 0 111 (001)^(A+1) 11111 (001)^c (11100111)^(t+1) 111 001001 B>
def M2p(ccells, Acells=None):
    return ('B', [1, 0, 0, 1, 0, 0, 1, 1, 1, run(TBM, t=1)] + list(TBM) + ccells + [1] * 5 + (Acells or [run((1, 0, 0), A=1)]) + [1, 0, 0]
            + [1, 1, 1, 0] + [0, 1] * 4 + [1, 0, 1] + [run(D4, d=1)] + YC + [1] + SC + [1, V_('l')], [BLANK], '>')
VH1_S = V([run(D4, d=1)], [run((1, 0, 0), A=1)], [0, 1], [run((1, 0, 1), c=1)], TT)
VH1_T = M2p([run((1, 0, 0), c=1)])
VH2_S = M2p([run((1, 0, 0) * 30, jj=1)] + [1, 0, 0] * 18)
ITEMS += [('VH1', VH1_S, VH1_T, dict(splits=1, maxstages=3000), ()), ('VH2', VH2_S, VH_T, dict(splits=1, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
# VH2 split at the moment before the last pass: Q3 far-first = l 1 (10)^2 1 (10)^(y+5) (1(10)^4)^(d+1) (10)^3 (110)^A 10 1^X
#   (00111111)^(t+2) 001001 B>,  X = 3c+5 (VH2a), and X = 5w+4 -> halt with (00111)^w (VH2b)
def Q3(xcells, Acells=None):
    return ('B', [1, 0, 0, 1, 0, 0, run((1, 1, 1, 1, 1, 1, 0, 0), t=1)] + [1, 1, 1, 1, 1, 1, 0, 0] * 2 + xcells + [0, 1] + (Acells or [run((0, 1, 1), A=1)])
            + [0, 1] * 3 + list(D4) + [run(D4, d=1)] + YC + [1] + SC + [1, V_('l')], [BLANK], '>')
# A shifted by one explicit block (A+1 in total): with a bare run the generated Coq script misses an alignment
VH2a_S = M2p([run((1, 0, 0), c=1)] + [1, 0, 0] * 3, Acells=[1, 0, 0, run((1, 0, 0), A=1)])
VH2a_T = Q3([run((1, 1, 1), c=1)] + [1] * 14, Acells=[0, 1, 1, run((0, 1, 1), A=1)])
VH2b_S = Q3([run((1,) * 5, w=1)] + [1] * 4)
VH2b_T = ('J', VH_T[1], [1] * 5 + [run((0, 0, 1, 1, 1), w=1), run((0, 0, 1, 0, 0, 1, 1, 1), t=1)]
          + [0, 0, 1, 0, 0, 1, 1, 1] * 2 + [0, 0, 1, 0, 0, 1, 0, 1, BLANK], '>')
ITEMS += [('VH2a', VH2a_S, VH2a_T, dict(splits=1, maxstages=3000), ()), ('VH2b', VH2b_S, VH2b_T, dict(splits=1, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
VHq_S = V([run(D4, d=1)], [run((1, 0, 0), A=1)], [0, 1], [run((1, 0, 1), c=1)] + [1, 0, 1] * 3, TT)
VHq_T = Q3([run((1, 1, 1), c=1)] + [1] * 14)
ITEMS += [('VHq', VHq_S, VHq_T, dict(splits=1, maxstages=3000), ())]
if os.environ.get('ITEM'):
    ITEMS = [it for it in ITEMS if it[0] == os.environ['ITEM']]
