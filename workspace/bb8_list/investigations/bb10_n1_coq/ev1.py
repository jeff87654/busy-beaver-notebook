import sys, time
from shapes import *
import mexp
from planner8 import show
EV = {
 'H':  (W(ONES(n=1), tok(1), Z(), tok(0, a=1)), W(tok(2), ONES(a=2), tok(4), Z(), ONES(n=1), Z(), tok(6))),
 'S0': (W(tok(2), ONES(M=1), tok(5), Z(), ONES(n=1), tok(1), tok(1), Z(), tok(0, a=1)),
        W(tok(2), tok(5), ONES(M=1), Z(), Z(), Z(), tok(3, a=1), ONES(n=1), Z(), tok(4))),
}
for name in sys.argv[1:]:
    S, T = EV[name]
    t0 = time.time()
    try:
        tree = mexp.explore(S, T, splits=3)
        print(name, 'OK %.1fs' % (time.time()-t0)); print('\n'.join(mexp.describe(tree))[:3000])
    except Exception as e:
        print(name, 'FAIL %.1fs' % (time.time()-t0), e)
