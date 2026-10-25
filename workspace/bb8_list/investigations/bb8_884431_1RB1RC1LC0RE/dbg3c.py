import sys
from guess3 import *
orig = engine.accelerate
cnt=[0]
def acc(S, depth=1):
    r = orig(S, depth)
    cnt[0]+=1
    if cnt[0] <= 12:
        print('ACCEL at', pl.show(S)[:170], 'd', depth, '->', None if r is None else (r['v'], r['inserts']), flush=True)
    return r
engine.accelerate = acc
try:
    engine.explore(M3(), G3())
except Exception as e:
    print('FAIL', str(e)[:100])
