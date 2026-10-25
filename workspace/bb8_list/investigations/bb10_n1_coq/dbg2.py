from common import *
import mexp
from planner8 import show
def H(left): return ('H', list(left), [BLANK], '>')
def B(ts, acc, far):
    left = list(acc) + tok(0)
    for t in reversed(ts): left += t
    return H(left + far)
def tok2(k, **var):
    return [1] + [0, 1] * k + ([run((0,1,0,1), **var)] if var else [])
for lab, S, T in [
   ('t0blank', B([tok(3)], tok(0, a=1), [BLANK]), B([tok(0)], tok2(8, a=1), [BLANK])),
   ('tgen', B([tok(3, t=1)], tok(0, a=1), [V('l')]), B([tok(0, t=1)], tok2(8, a=1), [V('l')])),
   ]:
    try:
        tree = mexp.explore(S, T, splits=3)
        print(lab, 'OK'); print('\n'.join(mexp.describe(tree))[:3000])
    except Exception as e:
        print(lab, 'FAIL', e)
