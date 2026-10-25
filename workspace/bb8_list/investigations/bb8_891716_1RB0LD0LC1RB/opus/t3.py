from w891 import *
import sys, time
segs = {
 'A0': (R['R3Am'][0], PS(2, {'k': 1}, 1, {'k': 1, 'r': 1}, 0, {})),
 'B0': (R['R3Bm'][0], PS(3, {'c': 1}, 1, {'c': 1}, 0, {})),
 'C0': (R['R3Cm'][0], PS(4, {'c': 1, 'm': 1}, 1, {'c': 1}, 0, {})),
 'A1': (PS(2, {}, 1, {'r': 1}, 0, {'k': 1}), R['R3Am'][1]),
 'B1': (PS(3, {}, 1, {}, 0, {'c': 1}), R['R3Bm'][1]),
 'C1': (PS(4, {'m': 1}, 1, {}, 0, {'c': 1}), R['R3Cm'][1]),
}
for nm in sys.argv[1:]:
    s, t = segs[nm]
    print('==', nm, pl.show(s), '=>', pl.show(t))
    t0 = time.time()
    try:
        tree = engine.explore(s, t)
        print('\n'.join(engine.describe(tree)))
    except Exception as e:
        print('FAIL', type(e).__name__, str(e)[:500])
    print('time %.1f' % (time.time() - t0))
