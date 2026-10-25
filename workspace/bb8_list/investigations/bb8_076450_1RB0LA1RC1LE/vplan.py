"""Planner runs for the F0 variant 1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG.
Ec(k, b, r) = 0^inf E> 0 1 1 0 (1010)^k (01)^b r   (= X(2k+1, b, r)); phases as in the related
machine 1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG (../bb8_076450_1RB1LE1RC1LE/gen_coq.py)."""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
VAR = "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG"
pl.set_tm(VAR)
T4 = (1, 0, 1, 0)
K = {'k': 1}; B = {'b': 1}
R = [V('r')]
def W(s):
    return [int(c) for c in s]
def E(side):
    return ('E', [BLANK], side, '>')
PH = {
    'IN': (E([0, 1, 1, 0] + mkrun(T4, K) + [0, 1] + mkrun((0, 1), B) + R),
           E([0, 1, 1, 0, 1, 0, 1, 0] + mkrun(T4, K) + mkrun((0, 1), B) + R)),
    'S5': (E([0, 1, 1, 0] + mkrun(T4, K) + [1] * 5 + R),
           E([0, 1] + [1, 0] * 5 + [0, 1, 0, 1] + mkrun((0, 1, 0, 1), K) + R)),
    'S4': (E([0, 1, 1, 0] + mkrun(T4, K) + [1] * 4 + [BLANK]),
           E([0, 1] + [1, 0] * 5 + [0, 1] + mkrun((0, 1, 0, 1), K) + [BLANK])),
    # X(a,0,e) -> X(3,0,1^(2a+1) 01)
    'Z0w': (E([0, 1, 1, 0] + mkrun(T4, K) + [BLANK]),
            E([0, 1] + [1, 0] * 3 + [1] * 3 + mkrun((1, 1, 1, 1), K) + W('01') + [BLANK])),
    # X(a,0,111 01) -> X(3,0,1^(2a+1) 0 11111 01)
    'E3w': (E([0, 1, 1, 0] + mkrun(T4, K) + W('11101') + [BLANK]),
            E([0, 1] + [1, 0] * 3 + [1] * 3 + mkrun((1, 1, 1, 1), K) + W('01111101') + [BLANK])),
    # X(a,0,11 0 11111 01) -> X(3,0,1^(2a+7) 01)
    'E2ww': (E([0, 1, 1, 0] + mkrun(T4, K) + W('1101111101') + [BLANK]),
             E([0, 1] + [1, 0] * 3 + [1] * 9 + mkrun((1, 1, 1, 1), K) + W('01') + [BLANK])),
    # X(a,0,11 01) -> X(3,0,1^(2a+3))
    'E2w': (E([0, 1, 1, 0] + mkrun(T4, K) + W('1101') + [BLANK]),
            E([0, 1] + [1, 0] * 3 + [1] * 5 + mkrun((1, 1, 1, 1), K) + [BLANK])),
}
if __name__ == '__main__':
    for w in [x for x in sys.argv[1:] if x in PH]:
        s, t = PH[w]
        try:
            drive(w, s, t, matchers=(), maxev=300, verbose=True)
        except Exception as e:
            print('EXC', type(e).__name__, e)
