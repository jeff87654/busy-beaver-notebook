import sys, time, traceback
from pieces import *
for nm, a, b in (('R3a', start3, M3), ('R3b', M3, G3)):
    t0 = time.time()
    try:
        tree = engine.explore(a, b)
        print(nm, 'OK %.1fs' % (time.time() - t0)); print('\n'.join(engine.describe(tree)))
    except Exception:
        print(nm, 'FAIL', traceback.format_exc()[-1500:])
