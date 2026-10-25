import time, engine, rules, oracle
from num import H, M
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
t0 = time.time()
for ctx in ([],):
    engine.memo.clear()
    s = ctx + [A] + [1] * 36 + [0, 6]
    try:
        r = engine.R(s, top=True)
        print('RESULT', r)
    except rules.Unknown as e:
        print('UNKNOWN', e)
    except RuntimeError as e:
        print('RUNTIME', e)
    print(engine.stats, oracle.stats, 'time %.1f' % (time.time() - t0))
