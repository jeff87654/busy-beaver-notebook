import sys, traceback
from rules884 import *
import engine
pl.set_tm(TM)
name = 'R4m'
for nm, s, t in rules():
    if nm != name: continue
    tc = pl.canon(t)
    ops, S, how = engine.run_until_stuck(s, tc, target=t)
    print('S1 =', pl.show(S))
    lp = engine.accelerate(S, 1)
    print('loop var', lp['v'], 'inserts', lp['inserts'])
    # full result: REM = 0
    res = engine.subst(lp['resultB'], 'dummy', (), 0)
    print('resultB =', pl.show(lp['resultB']))
    # after last round
    ops, C, how = engine.run_until_stuck(lp['resultB'], None)
    print(how, 'after last round:', pl.show(C))
    print(' crossing:', pl.try_crossing(C)[1] if pl.try_crossing(C)[0] is None else 'ok')
