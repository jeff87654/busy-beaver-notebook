import sys, time, traceback
import rules_r4
from rules884 import *
import engine
pl.set_tm(TM)
for name, s, t, prog in rules_r4.pieces():
    t0=time.time()
    try:
        tree = engine.explore(s, t); print(name, 'ok %.1fs' % (time.time()-t0))
    except Exception as e:
        print(name, 'FAIL', type(e).__name__, str(e)[:200])
