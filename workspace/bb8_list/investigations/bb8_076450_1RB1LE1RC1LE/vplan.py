"""Planner runs for the F0 variant 1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_0RA0RG.
VE(k, b, r) = 0^inf E> 0 1 (1010)^k (01)^b r   (= X(2k, b, r))"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
VAR = "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_0RA0RG"
pl.set_tm(VAR)
T4 = (1, 0, 1, 0)
K = {'k': 1}; B = {'b': 1}
R = [V('r')]
def E(side):
    return ('E', [BLANK], side, '>')
def W(s):
    return [int(c) for c in s]
P1 = [0, 1, 1, 0, 1, 0]          # 0 1 (1010)^(k+1) = 0 1 1010 (1010)^k
PH = {
    # X(2k+2, b+1, r) -> X(2k+4, b, r)
    'IN': (E(P1 + mkrun(T4, K) + [0, 1] + mkrun((0, 1), B) + R),
           E(P1 + [1, 0, 1, 0] + mkrun(T4, K) + mkrun((0, 1), B) + R)),
    # X(2k+2,0,11111 r) -> X(6, 2k+2, r)
    'S5': (E(P1 + mkrun(T4, K) + [1] * 5 + R),
           E([0, 1] + [1, 0] * 6 + [0, 1, 0, 1] + mkrun((0, 1, 0, 1), K) + R)),
    # X(2k+2,0,1111 r) -> X(6, 2k+1, 0 r)
    'S4': (E(P1 + mkrun(T4, K) + [1] * 4 + R),
           E([0, 1] + [1, 0] * 6 + [0, 1] + mkrun((0, 1, 0, 1), K) + [0] + R)),
    # c=2 blank: X(2k+2,0,11) -> X(4,0,1^(4k+4))
    'E2b': (E(P1 + mkrun(T4, K) + [1, 1, BLANK]),
            E([0, 1] + [1, 0] * 4 + [1] * 4 + mkrun((1, 1, 1, 1), K) + [BLANK])),
    # c=1 blank: X(2k+2,0,1) -> X(4,0,1^(4k+7))
    'E1b': (E(P1 + mkrun(T4, K) + [1, BLANK]),
            E([0, 1] + [1, 0] * 4 + [1] * 7 + mkrun((1, 1, 1, 1), K) + [BLANK])),
    # c=3 blank: X(2k+2,0,111) -> X(4,0,1^(4k+3) 010111)
    'E3b': (E(P1 + mkrun(T4, K) + [1, 1, 1, BLANK]),
            E([0, 1] + [1, 0] * 4 + [1, 1, 1] + mkrun((1, 1, 1, 1), K) + W('010111') + [BLANK])),
    # c=2, 010111: X(2k+2,0,11 010111) -> X(4,0,1^(4k+5) 0111)
    'E2w': (E(P1 + mkrun(T4, K) + W('11010111') + [BLANK]),
            E([0, 1] + [1, 0] * 4 + [1] * 5 + mkrun((1, 1, 1, 1), K) + W('0111') + [BLANK])),
    # c=0, 0 0111: X(2k+2,0,00111) -> X(4,0,1^(4k+6))
    'E0x': (E(P1 + mkrun(T4, K) + W('00111') + [BLANK]),
            E([0, 1] + [1, 0] * 4 + [1] * 6 + mkrun((1, 1, 1, 1), K) + [BLANK])),
}
if __name__ == '__main__':
    for w in [x for x in sys.argv[1:] if x in PH]:
        s, t = PH[w]
        try:
            drive(w, s, t, matchers=(), maxev=300, verbose=True)
        except Exception as e:
            print('EXC', type(e).__name__, e)
