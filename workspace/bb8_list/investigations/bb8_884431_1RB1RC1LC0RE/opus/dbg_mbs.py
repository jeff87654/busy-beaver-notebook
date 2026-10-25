import sys, time, traceback
from pieces import *
orig_acc, orig_exp, orig_run = engine.accelerate, engine.explore, engine.run_until_stuck
def acc(S, depth=1):
    r = orig_acc(S, depth)
    print('  ACCEL d%d at %s -> %s' % (depth, pl.show(S), None if r is None else (r['v'], r['inserts'], [x[0] for x in r['round']])), flush=True)
    return r
def exp(start, target, depth=2, splits=4, path='root'):
    print('EXPLORE', path, 'splits', splits, ':', pl.show(start)[:250], flush=True)
    return orig_exp(start, target, depth, splits, path)
engine.accelerate = acc; engine.explore = exp
a, b = engine.subst(M3, 'b', (('b', 1),), 1), engine.subst(G3, 'b', (('b', 1),), 1)
try:
    tree = engine.explore(a, b)
except Exception as e:
    print('FAIL', str(e)[:300])
