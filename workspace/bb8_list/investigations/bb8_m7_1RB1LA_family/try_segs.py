import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from segs import *
names = sys.argv[1:] or list(segs())
S = segs()
S['R4m'] = (R['R4m'][0], R['R4m'][1], True)
for nm in names:
    s, t, prog = S[nm]
    t0 = time.time()
    try:
        tree = engine.explore(s, t)
        print(nm, 'OK', '%.1fs' % (time.time() - t0))
        print('\n'.join(engine.describe(tree))[:3000])
    except Exception as e:
        print(nm, 'FAIL', type(e).__name__, str(e)[:300])
