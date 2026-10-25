"""python drv12.py NAME [lit] [explore]: validate (literally) / explore event NAME of evs12.EV."""
import sys, time, random
from evs12 import *
import mexp
name = sys.argv[1]
S, T = EV[name][:2]
POS = frozenset(EV[name][2]) if len(EV[name]) > 2 else frozenset()
if 'lit' in sys.argv:
    vs = sorted(engine.vars_of(S) | engine.vars_of(T))
    rnd = random.Random(1)
    ok = True
    for _ in range(6):
        vals = {v: rnd.randint(0, 6) for v in vs}
        r = validate.reaches(S, T, vals, max_steps=3_000_000)
        print('literal', vals, '->', r)
        ok = ok and r is not None
    print(name, 'LIT', 'OK' if ok else 'FAIL')
if 'explore' in sys.argv:
    t0 = time.time()
    try:
        tree = mexp.explore(S, T, splits=4, positive=POS)
        print(name, 'OK %.1fs' % (time.time() - t0))
    except Exception as e:
        print(name, 'FAIL %.1fs' % (time.time() - t0), e)
