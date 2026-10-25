import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
# PASS: G(j+2, T) -> G(j+1, 0111 T), T = 0 1 1 1 w
T = [0, 1, V('w')]
start = ('A', [BLANK], pl.norm_side([0] + mkrun((1, 1), {'j': 1}, 2) + T), '>')
tgt = ('A', [BLANK], pl.norm_side([0] + mkrun((1, 1), {'j': 1}, 1) + [0, 1, 1, 1] + T), '>')
try:
    tree = engine.explore(start, tgt)
    print('OK'); print('\n'.join(engine.describe(tree)))
except Exception:
    print(traceback.format_exc()[-800:])
