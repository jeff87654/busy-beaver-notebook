import sys
from guess3 import *
S = M3()
v='b'
v2='b0'
P = engine.subst(S, v, ((v2,1),), 1)
S1 = engine.subst(S, v, ((v2,1),), 0)
print('P =', pl.show(P))
ops, C, how = engine.run_until_stuck(P, None)
print(how, 'C =', pl.show(C)); print(ops)
print('S1 =', pl.show(S1))
print(engine.match_shift(S1, C))
print(pl.try_crossing(C))
print('=== try_loop depth 1')
import traceback
try:
    lp = engine.try_loop(S, 'b', 1)
    print('lp', None if lp is None else (lp['inserts'], [r[0] for r in lp['round']]))
except Exception:
    print(traceback.format_exc()[-600:])
lp2 = engine.accelerate(S, 1)
print('accel', None if lp2 is None else (lp2['v'], lp2['inserts']))
