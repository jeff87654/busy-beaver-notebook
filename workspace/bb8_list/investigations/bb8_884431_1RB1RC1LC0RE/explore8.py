import sys, time, traceback
from rules884 import *
import engine
pl.set_tm(TM)
# R4 stage 1: start -> M(n,b)
start4 = cfg(kc(({'b': 1}, 0), [], mkrun(E, {'n': 1}, 0) + [1, 1, 1, BLANK]))
# M(n,b) = (0101)^b <A  (11)^n 1111 0 1^8 BLANK ; head cell = last cell of b-run (stream order: block 1010 nearest-first)
M = ('A', [('run', (1, 0, 1, 0), (('b', 1),)), BLANK], [('run', (1, 1), (('n', 1),))] + [1, 1, 1, 1, 0] + [1] * 8 + [BLANK], '<')
tgt4 = cfg(kc(({}, 0), arun({}, 1), mkrun((1, 1) + U, {'n': 1}, 0) + mkrun((1, 1, 1, 1), {'b': 1}, 1) + [1, 1, 1, BLANK]))
t0 = time.time()
which = sys.argv[1]
orig = engine.accelerate
def acc(S, depth=1):
    r = orig(S, depth)
    print('ACCEL at', pl.show(S), 'depth', depth, '->', None if r is None else (r['v'], r['inserts']), flush=True)
    return r
engine.accelerate = acc
try:
    if which == '1':
        tree = engine.explore(start4, M)
    else:
        tree = engine.explore(M, tgt4)
    print('OK %.1fs' % (time.time()-t0))
    print('\n'.join(engine.describe(tree)))
except Exception:
    print(traceback.format_exc()[-600:])
