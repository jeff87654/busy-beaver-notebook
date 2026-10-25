import sys, time
from rules884 import *
import engine
pl.set_tm(TM)
which = sys.argv[1:] 
for name, s, t in rules():
    if which and name not in which: continue
    t0 = time.time()
    try:
        tree = engine.explore(s, t)
        print(name, 'OK', '%.1fs' % (time.time()-t0))
        print('\n'.join(engine.describe(tree)))
    except Exception as e:
        print(name, 'FAIL', type(e).__name__, e)
