import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
name = sys.argv[1]
for nm, s, t in rules():
    if nm != name: continue
    print(pl.show(s))
    # run stage by stage to see where it gets stuck
    tc = pl.canon(t)
    ops, cfg, how = engine.run_until_stuck(s, tc, target=t)
    print(how, pl.show(cfg)); print(ops)
