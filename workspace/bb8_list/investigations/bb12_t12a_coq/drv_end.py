"""python drv_end.py NAME [lit] [explore] [show]: validate (literally, random values 0..6) / explore event NAME of evs_end.EVE."""
import sys, time, random
from evs_end import *
import mexp
mexp.MAXLEN = 200
from probe import next_b, fast_check
name = sys.argv[1]
S, T = EVE[name][:2]
POS = frozenset(EVE[name][2]) if len(EVE[name]) > 2 else frozenset()
if 'lit' in sys.argv:
    vs = sorted(engine.vars_of(S) | (engine.vars_of(T) if T else set()))
    rnd = random.Random(1)
    ok = True
    for _ in range(8):
        vals = {v: rnd.randint(0, 6) for v in vs}
        if T is None:
            r = next_b(S, vals)
            print('literal', vals, '->', r[:3])
            ok = ok and r[0] == 'HALT'
            continue
        r = fast_check(S, T, vals)
        print('literal', vals, '->', r[:2])
        if not r[0]:
            print('   actual:', r[2])
        ok = ok and r[0]
    print(name, 'LIT', 'OK' if ok else 'FAIL')
if 'explore' in sys.argv:
    t0 = time.time()
    try:
        tree = mexp.explore(S, T, splits=4, positive=POS)
        print(name, 'OK %.1fs' % (time.time() - t0))
        if 'show' in sys.argv:
            print('\n'.join(mexp.describe(tree)))
    except Exception as e:
        print(name, 'FAIL %.1fs' % (time.time() - t0), e)
