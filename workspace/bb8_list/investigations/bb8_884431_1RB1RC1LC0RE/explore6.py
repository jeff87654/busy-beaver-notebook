import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
n = int(sys.argv[1])
# R4 with concrete n
start4 = kc(({'b': 1}, 0), [], list(E)*n + [1, 1, 1, BLANK])
tgt4 = kc(({}, 0), arun({}, 1), list((1, 1) + U)*n + mkrun((1, 1, 1, 1), {'b': 1}, 1) + [1, 1, 1, BLANK])
orig = engine.accelerate
def acc(S, depth=1):
    r = orig(S, depth)
    print('ACCEL at', pl.show(S), 'depth', depth, '->', None if r is None else (r['v'], r['inserts']))
    return r
engine.accelerate = acc
try:
    tree = engine.explore(cfg(start4), cfg(tgt4))
    print('\n'.join(engine.describe(tree)))
except Exception:
    print(traceback.format_exc()[-400:])
