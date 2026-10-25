import sys
sys.path.insert(0, '.')
from evs_end import *
import mexp
from planner8 import show
S, T = EVE[sys.argv[1]][:2]
cfg = S
while True:
    ops, cfg, how = mexp.run_stuck(cfg, T)
    lp = mexp.find_loop(cfg, 1)
    if lp.v_at.startswith('j'): break
    cfg = lp.after()
mexp.debug_loop(cfg, depth=1, width=4000)
