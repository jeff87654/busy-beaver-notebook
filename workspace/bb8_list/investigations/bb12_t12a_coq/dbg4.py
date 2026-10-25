from common import *
import mexp, time
from planner8 import show
exec(open('dbg2.py').read().split('for lab')[0])
for lab, S, T in [
   ('t0blank', B([tok(3)], tok(0, a=1), [BLANK]), B([tok(0)], tok2(8, a=1), [BLANK])),
   ('tgen', B([tok(3, t=1)], tok(0, a=1), [V('l')]), B([tok(0, t=1)], tok2(8, a=1), [V('l')])),
   ]:
    t0=time.time()
    try:
        tree = mexp.explore(S, T, splits=3, maxstages=300)
        print(lab, 'OK %.1fs' % (time.time()-t0)); print('\n'.join(mexp.describe(tree))[:1500])
    except Exception as e:
        print(lab, 'FAIL', e)
