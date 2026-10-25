import time, sys, engine, rules, oracle
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
def fmt(t):
    return ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in t)
for w in [12, 13, 14, 15, 16, 17, 18, 19, 22, 24, 26, 28, 30, 32]:
    engine.memo.clear()
    t0 = time.time()
    s = [A] + [1] * w + [0, 6]
    try:
        r = engine.R(s, top=True)
        out = 'RESULT ' + fmt(r)
    except rules.Unknown as e:
        out = 'UNKNOWN ' + str(e).split(' | ')[0][:60] + ' | ' + fmt(getattr(e, 'lst', []))[-60:]
    except RuntimeError as e:
        out = 'RUNTIME ' + str(e)[:80]
    print('w=%2d %6.1fs %s' % (w, time.time() - t0, out))
    sys.stdout.flush()
