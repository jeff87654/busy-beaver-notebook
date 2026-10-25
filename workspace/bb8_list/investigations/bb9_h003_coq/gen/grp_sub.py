"""C7 cascade sub-steps (X'), generic far end l.  D0f t L P s y l (Lift.v), nearest-first:
   1001 TB^t 11 1^L (001)^P 110 (01)^y 101 (01)^s 1 l.   Fitted by tools/fitsub.py (all P residues, s, y free):
   r=1: L=5J+61 -> L'=3J+32, P'=P-4, s'=y, y'=J+16, l' = (01)^s 1 l
   r=3: L=5J+63 -> L'=3J+35, P'=P-4, s'=2, y'=J+13, l' = (01)^y 1 (01)^s 1 l
   r=0: L=5J+60 -> L'=3J+32, P'=P-6, s'=4, y'=J+14, l' = (01)^y 1 (01)^s 1 l
   r=4: L=5J+64 -> L'=3J+32, P'=P-6, s'=6, y'=J+14, l' = (01)^y 1 (01)^s 1 l      (t' = t+2 always)"""
import sys
from common import *
from shapes import *
def d0(tc, Lc, Pc, yc, sc, far):
    return ('B', [1, 0, 0, 1] + list(TB) * tc + [run(TB, t=1), 1, 1] + Lc + Pc + [1, 1, 0] + yc + [1, 0, 1] + sc + [1] + far,
            [BLANK], '>')
U2 = (0, 1)
def Lr(k, c): return [run((1,) * k, J=1)] + [1] * c
P0 = [run((0, 0, 1), p=1)]
def Pk(k): return [0, 0, 1] * k + P0
Y = [run(U2, y=1)]; S = [run(U2, s=1)]; L = [V('l')]
def conc(n): return [0, 1] * n
ITEMS_ALL = {
 'sub1': ('SUB1', d0(0, Lr(5, 61), Pk(4), Y, S, L),
          d0(2, Lr(3, 32), P0, [run(U2, J=1)] + conc(16), Y, [run(U2, s=1)] + [1] + L)),
 'sub3': ('SUB3', d0(0, Lr(5, 63), Pk(4), Y, S, L),
          d0(2, Lr(3, 35), P0, [run(U2, J=1)] + conc(13), conc(2), [run(U2, y=1), 1, run(U2, s=1), 1] + L)),
 'sub0': ('SUB0', d0(0, Lr(5, 60), Pk(6), Y, S, L),
          d0(2, Lr(3, 32), P0, [run(U2, J=1)] + conc(14), conc(4), [run(U2, y=1), 1, run(U2, s=1), 1] + L)),
 'sub4': ('SUB4', d0(0, Lr(5, 64), Pk(6), Y, S, L),
          d0(2, Lr(3, 32), P0, [run(U2, J=1)] + conc(14), conc(6), [run(U2, y=1), 1, run(U2, s=1), 1] + L)),
}
def mk(k):
    n, S0, T0 = ITEMS_ALL[k]
    return [(n, S0, T0, dict(splits=2, maxstages=400), ())]
ITEMS = []
