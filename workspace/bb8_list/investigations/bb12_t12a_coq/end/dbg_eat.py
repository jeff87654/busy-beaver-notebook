import sys, time
sys.path.insert(0, '.')
from evs_end import *
import mexp
from planner8 import show
S, T = EVE[sys.argv[1]][:2]
t0 = time.time()
ops, cfg, how = mexp.run_stuck(S, T)
print(how, time.time() - t0, sum(o[1] for o in ops if o[0] == 'steps'))
print(show(cfg)[:1500])
if how == 'stuck':
    mexp.debug_loop(cfg, depth=1, width=1500)
