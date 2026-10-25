"""Group 'end': endgame bounded rules (class-b counter engine + the halt).
  DEC<C>: Kt(ctx, C, 1^(z+1); 1; r; t) -->+ Kt(ctx, C-3, 2r+3, 1^z; 1; 2; t)   (one counter decrement; r = accumulator run)
          for C in {6, 3}; deposits the accumulator as the token D(2r+3) = T(R) (= 6R+7 when r = 3R+2) and decrements C by 3.
  HALT  : Kt(ctx, 0(=D0), 1^(z+1); 1; r+1; t) -->+ <H reading 1>  (the C=0 ending: head enters the nearest far token
          D(a+1) and halts in state H reading 1, leaving a run of 2r+... ones).  Here the nearest far token has value a+1
          (so the halt tape keeps (10)^a of it), the accumulator run is r+1, the near zeros z+1, t tail blocks.
          Halt tape (nearest far..head..right): .. (110)^z 1 0 1 (10)^a 1 l  <H>  1 1 1 1 0 (1010)^r 0 1 0 1 1 (TB')^t 0 1
          (TB' = 11001001).  ones at the halt >= the (1010)^r run = 2r ones = 6R+2 (when r = 3R+1), dominated by R = R_last."""
from common import *
from shapes import *

def dec(C):
    S = K(accr(0, 'r'), tok(1), list(Z) + [run(Z, z=1)] + tok(C))
    T = K(accr(2), tok(1), [run(Z, z=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(C - 3))
    return ('DEC%d' % C, S, T, dict(positive=frozenset(('r',))), ('r',))

def halt_item():
    # accumulator (01)^(r+1); near (101)^(z+1); C = 0 token D(0); far token D(a+1); far side l.
    S = ('B',
         tailpart()
         + [0, 1, run((0, 1), r=1)] + [1]                       # acc (01)^(r+1), then D(1)=m
         + [run((1, 0, 1), z=1), 1, 0, 1] + [1]                 # near (101)^(z+1), then D(0)
         + [1, 0, 1, run((0, 1), a=1)]                          # D(a+1)
         + [1, V('l')], [BLANK], '>')
    T = ('H',
         [1, 1, run((0, 1, 1), z=1), 1, 0, 1, run((0, 1), a=1), 1, V('l')],
         [1, 1, 1, 1, 0, run((1, 0, 1, 0), r=1), 0, 1, 0, 1, 1, run((1, 1, 0, 0, 1, 0, 0, 1), t=1), 0, 1, BLANK],
         '<')
    return ('HALT', S, T, dict(splits=6), ())

ITEMS = [dec(6), dec(3), halt_item()]
