import sys, time, traceback
from guess3 import *
t0=time.time()
for nm, (a, b) in (('R3a', (start3, M3())), ('R3b', (M3(), G3()))):
    try:
        tree = engine.explore(a, b)
        print(nm, 'OK %.1fs' % (time.time()-t0))
        d = engine.describe(tree); print(len(d), 'lines'); print('\n'.join(x[:200] for x in d[:14]))
    except Exception:
        print(nm, 'FAIL', traceback.format_exc()[-500:])
