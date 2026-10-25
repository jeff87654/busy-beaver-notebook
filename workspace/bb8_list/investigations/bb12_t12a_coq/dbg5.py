import sys
from evs import *
import mexp
from planner8 import show
S, T = EV[sys.argv[1]][:2]
ops, cfg, how = mexp.run_stuck(S, T)
print(show(cfg))
mexp.debug_loop(cfg, depth=2, width=400)
