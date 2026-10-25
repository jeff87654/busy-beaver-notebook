import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
M = ('A', [('run', (1, 0, 1, 0), (('b', 1),)), BLANK], [('run', (1, 1), (('n', 1),))] + [1, 1, 1, 1, 0] + [1] * 8 + [BLANK], '<')
G = ('A', [BLANK], pl.norm_side(mkrun((1, 1), {'n': 1}, 2) + [0] + mkrun((1, 1, 1, 1), {'b': 1}, 2) + [BLANK]), '<')
t0=time.time()
try:
    tree = engine.explore(M, G)
    print('OK %.1fs' % (time.time()-t0)); print('\n'.join(engine.describe(tree)))
except Exception:
    print(traceback.format_exc()[-800:])
