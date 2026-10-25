import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
from explore import TM, E, R, A, B
K = {'k': 1}
T4 = (1, 0, 1, 0)
PH = {}
PH['IN'] = (E([0, 1, 1, 0], mkrun(T4, K), [0, 1] + mkrun((0, 1), B), R),
            E([0, 1, 1, 0, 1, 0, 1, 0], mkrun(T4, K), mkrun((0, 1), B), R))
PH['S5'] = (E([0, 1, 1, 0], mkrun(T4, K), [], [1]*5 + R),
            E([0, 1] + [1, 0]*5, [], [0, 1, 0, 1] + mkrun((0, 1, 0, 1), K), R))
PH['S4'] = (E([0, 1, 1, 0], mkrun(T4, K), [], [1]*4 + [BLANK]),
            E([0, 1] + [1, 0]*5, [], [0, 1] + mkrun((0, 1, 0, 1), K), [BLANK]))
PH['Z0'] = (E([0, 1, 1, 0], mkrun(T4, K), [], [BLANK]),
            E([0, 1] + [1, 0]*3, [], [1]*5 + mkrun((1, 1, 1, 1), K), [BLANK]))
PH['Z1'] = (E([0, 1, 1, 0], mkrun(T4, K), [], [1, BLANK]),
            E([0, 1] + [1, 0]*3, [], [1]*7 + mkrun((1, 1, 1, 1), K), [BLANK]))
for w in [x for x in sys.argv[1:] if x in PH]:
    s, t = PH[w]
    try:
        drive(w, s, t, matchers=(), maxev=300, verbose=True)
    except Exception as e:
        print('EXC', type(e).__name__, e)
