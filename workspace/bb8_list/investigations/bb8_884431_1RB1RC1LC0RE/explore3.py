import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
name = sys.argv[1]; v = sys.argv[2]
for nm, s, t in rules():
    if nm != name: continue
    tc = pl.canon(t)
    ops, cfg, how = engine.run_until_stuck(s, tc, target=t)
    S = cfg
    print('S =', pl.show(S))
    v2 = engine.fresh(v)
    P = engine.subst(S, v, ((v2, 1),), 1)
    S1 = engine.subst(S, v, ((v2, 1),), 0)
    print('P =', pl.show(P))
    ops, C, how = engine.run_until_stuck(P, None)
    print(how, 'C =', pl.show(C)); print(ops)
    print('S1 =', pl.show(S1))
    m = engine.match_shift(S1, C)
    print('match', m)
