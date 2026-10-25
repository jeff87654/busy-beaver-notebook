import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG"
if len(sys.argv) > 1 and sys.argv[1].startswith('--tm='):
    TM = sys.argv.pop(1)[5:]
pl.set_tm(TM)
R = [V('r')]
A = {'a': 1}; B = {'b': 1}
def E(pre, a_run, b_run, tail):
    return ('E', [BLANK], pre + a_run + b_run + tail, '>')
PH = {}
# inner: E(a, b+1, r) -> E(a+2, b, r)
PH['IN'] = (E([0, 1], mkrun((1, 0), A), [0, 1] + mkrun((0, 1), B), R),
            E([0, 1, 1, 0, 1, 0], mkrun((1, 0), A), mkrun((0, 1), B), R))
# small reset: E(a, 0, 11111 r) -> E(5, a+1, r)
PH['S5'] = (E([0, 1], mkrun((1, 0), A), [], [1]*5 + R),
            E([0, 1] + [1, 0]*5, [], [0, 1] + mkrun((0, 1), A), R))
# c=4 end: E(a, 0, 1111 0^inf) -> E(5, a, 0^inf)
PH['S4'] = (E([0, 1], mkrun((1, 0), A), [], [1]*4 + [BLANK]),
            E([0, 1] + [1, 0]*5, [], mkrun((0, 1), A), [BLANK]))
# c=0 end: E(a, 0, 0^inf) -> E(3, 0, 1^(2a+3) 0^inf)
PH['Z0'] = (E([0, 1], mkrun((1, 0), A), [], [BLANK]),
            E([0, 1] + [1, 0]*3, [], [1]*3 + mkrun((1, 1), A), [BLANK]))
# c=1 end: E(a, 0, 1 0^inf) -> E(3, 0, 1^(2a+5) 0^inf)
PH['Z1'] = (E([0, 1], mkrun((1, 0), A), [], [1, BLANK]),
            E([0, 1] + [1, 0]*3, [], [1]*5 + mkrun((1, 1), A), [BLANK]))
if __name__ == '__main__':
    for w in [x for x in sys.argv[1:] if x in PH]:
        s, t = PH[w]
        try:
            drive(w, s, t, matchers=(), maxev=300, verbose=True)
        except Exception as e:
            print('EXC', type(e).__name__, e)
