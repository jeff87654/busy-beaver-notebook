import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = "1RB1RD_1LC1LF_1RH1RA_1LE1LG_0RB1LE_1RC0LG_1RA0LB_---1RF"
pl.set_tm(TM)
D = (1, 0, 0)
A = {'a': 1}; B = {'b': 1}
R = [V('r')]
def P(a, b, tail, bconst=0, aconst=0):
    return ('C', [BLANK], [0] + mkrun(D, a, aconst) + [1, 0] + mkrun(D, b, bconst) + tail, '>')
ONE = (1,)
K = {'k': 1}; M = {'m': 1}
def Q(a, b, j, aconst=0, bconst=0, jconst=0):
    return ('C', [BLANK], [0] + mkrun(D, a, aconst) + [1, 0] + mkrun(D, b, bconst) + [1, 0, 1] + j + R, '>')
PH = {
 'P2': (P(A, {}, [1,1,1] + mkrun(ONE, K) + R),
        ('C', [BLANK], [0,1,0,0,1,0] + mkrun(D, A) + [1,0,1] + mkrun(ONE, K) + R, '>')),
 'Q1': (('C', [BLANK], [0] + mkrun(D, A) + [1, 0] + mkrun(D, B, 1) + [1,0,1] + R, '>'),
        ('C', [BLANK], [0] + mkrun(D, A, 2) + [1, 0] + mkrun(D, B) + [1,0,1] + R, '>')),
 'Q2': (('C', [BLANK], [0] + mkrun(D, A) + [1, 0, 1, 0, 1] + mkrun(ONE, K) + R, '>'),
        ('C', [BLANK], [0] + mkrun(D, A, 2) + [1] + mkrun(ONE, K) + R, '>')),
 'X1': (('C', [BLANK], [0] + mkrun(D, A) + [1,1,1,1,1,1] + mkrun(ONE, M) + R, '>'),
        ('C', [BLANK], [0,1,0,0,1,0] + mkrun(D, A) + [1,1,1,1] + mkrun(ONE, M) + R, '>')),
 'X0': (('C', [BLANK], [0] + mkrun(D, A, 1) + [1,1] + [BLANK], '>'),
        ('C', [BLANK], [0,1,0,0,1,0] + mkrun(D, A, 1) + [BLANK], '>')),
 'P0': (('C', [BLANK], [0] + mkrun(D, A) + [1, 0] + mkrun(D, B, 2) + [BLANK], '>'),
        ('C', [BLANK], [0] + mkrun(D, A, 2) + [1, 0] + mkrun(D, B, 1) + [BLANK], '>')),
 'R0': (('C', [BLANK], [0] + mkrun(D, A, 1) + [1, 0, 1, 0, 0, BLANK], '>'),
        ('C', [BLANK], [0,1,0,0,1,0] + [1]*2 + mkrun((1,1,1), {'a':1}) + [1]*6 + [BLANK], '>')),
 # P1: P(a,b+1,k+1) -> P(a+2,b,k+1)
 'P1': (P(A, B, [1] + R, bconst=1), P(A, B, [1] + R, aconst=2)),
}
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a in PH]:
        s, t = PH[w]
        drive(w, s, t, maxev=200, verbose=True)
