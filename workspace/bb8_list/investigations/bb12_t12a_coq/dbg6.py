import sys
from evs import *
import mexp
from planner8 import show
S, T = EV[sys.argv[1]][:2]
ops, cfg, how = mexp.run_stuck(S, T)
v = sys.argv[2]
v2 = mexp.fresh(v)
P = mexp.subst(cfg, v, ((v2, 1),), 1)
c = P
for i in range(12):
    ops, c, how = mexp.run_stuck(c)
    print(i, how, sum(o[1] for o in ops if o[0]=='steps'), show(c)[:300])
    if how != 'stuck': break
    lp = mexp.find_loop(c, 1)
    print('   inner', lp and (lp.v_at, lp.use_arg()))
    if lp is None: break
    c = lp.after()
