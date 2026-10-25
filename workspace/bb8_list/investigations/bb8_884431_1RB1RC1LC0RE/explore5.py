import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
name = sys.argv[1]
orig = engine.accelerate
def acc(S, depth=1):
    print('ACCEL at', pl.show(S), 'depth', depth)
    r = orig(S, depth)
    print('   ->', None if r is None else (r['v'], r['inserts']))
    return r
engine.accelerate = acc
for nm, s, t in rules():
    if nm != name: continue
    try:
        tree = engine.explore(s, t)
        print('\n'.join(engine.describe(tree)))
    except Exception:
        print(traceback.format_exc()[-300:])
