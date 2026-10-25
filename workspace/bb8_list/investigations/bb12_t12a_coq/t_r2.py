from common import *
import mexp, time
from planner8 import show
exec(open('t_pass.py').read().split('for lab')[0])
ONES = lambda **v: [run((1,0,1), **v)]
for lab, S, T in [
  ('R2', W(tok(3, t=1), ONES(k=1), tok(1), tok(0), tok(0, a=1)), W(tok(0, t=1), tok(3, a=1), ONES(k=1), tok(0), tok(4))),
]:
    t0 = time.time()
    try:
        tree = mexp.explore(S, T, splits=3)
        print(lab, 'OK %.1fs' % (time.time()-t0)); print('\n'.join(mexp.describe(tree))[:4000])
    except Exception as e:
        print(lab, 'FAIL %.1fs' % (time.time()-t0), e)
