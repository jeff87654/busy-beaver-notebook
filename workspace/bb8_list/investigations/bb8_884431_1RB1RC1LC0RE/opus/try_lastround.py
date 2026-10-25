import sys, time, traceback
from pieces import *
lp = engine.accelerate(M3, 1)
print('loop on', lp['v'], lp['v2'], lp['inserts'], [r[0] for r in lp['round']])
print('resultB', pl.show(lp['resultB']))
tg = engine.subst(G3, 'b', ((lp['v2'], 1),), 1)
print('target ', pl.show(tg))
t0 = time.time()
try:
    tree = engine.explore(lp['resultB'], tg)
    print('OK %.1fs' % (time.time() - t0)); print('\n'.join(l for l in engine.describe(tree) if 'ops:' not in l))
except Exception:
    print('FAIL %.1fs' % (time.time() - t0), traceback.format_exc()[-600:])
