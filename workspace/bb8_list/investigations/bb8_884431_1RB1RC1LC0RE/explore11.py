import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
name = sys.argv[1]
orig = engine.accelerate
cnt=[0]
def acc(S, depth=1):
    r = orig(S, depth)
    cnt[0]+=1
    if cnt[0] <= int(sys.argv[2]):
        print('ACCEL at', pl.show(S)[:150], 'd', depth, '->', None if r is None else (r['v'], r['inserts']), flush=True)
    if cnt[0] > int(sys.argv[2]): sys.exit(0)
    return r
engine.accelerate = acc
for nm, s, t in rules():
    if nm != name: continue
    try:
        tree = engine.explore(s, t)
    except SystemExit: pass
    except Exception:
        print(traceback.format_exc()[-300:])
