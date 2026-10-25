import sys, time, traceback
from pieces import *
orig_acc, orig_exp = engine.accelerate, engine.explore
def acc(S, depth=1):
    r = orig_acc(S, depth)
    print('  ACCEL d%d at %s -> %s' % (depth, pl.show(S), None if r is None else (r['v'], r['inserts'], [x[0] for x in r['round']])), flush=True)
    return r
def exp(start, target, depth=2, splits=4, path='root'):
    print('EXPLORE', path, 'splits', splits, ':', pl.show(start)[:200], flush=True)
    return orig_exp(start, target, depth, splits, path)
engine.accelerate = acc; engine.explore = exp
if len(sys.argv) > 1 and sys.argv[1] == "4": M3, G3 = start4, G
try:
    tree = engine.explore(start3 if len(sys.argv) < 2 else M, G3 if len(sys.argv) < 2 else G)
except Exception as e:
    print('FAIL', str(e)[:300])
