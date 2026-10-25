import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
name = sys.argv[1]
for nm, s, t in rules():
    if nm != name: continue
    try:
        tree = engine.explore(s, t)
        print('\n'.join(engine.describe(tree)))
    except Exception:
        traceback.print_exc()
