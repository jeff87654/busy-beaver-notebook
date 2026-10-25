"""engine (with a low huge-threshold, so that jumps and residues are exercised) vs exact big-integer brute force"""
import random, time
import num, engine, rules
from num import H, M, is_huge
random.seed(21)
agree = dis = skip = 0; t0 = time.time()
for trial in range(400):
    s = [random.randint(100, 700)] + random.choice([[0, 0], [2, 0, 0], [0, 0, 0], [3, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0, 0], [2, 0, 3, 0, 0]]) + [random.randint(2, 9)]
    # exact brute force
    num.EXACT = True
    t = list(s); n = 0; ok = True
    try:
        while True:
            try:
                ev = rules.classify(t)
            except rules.Need:
                break
            t = ev.newlist; n += 1
            if n > 200000 or max(v.bit_length() for v in t if isinstance(v, int)) > 200000:
                ok = False; break
    except (rules.Unknown, OverflowError):
        ok = False
    num.EXACT = False
    if not ok:
        skip += 1; continue
    # engine with low threshold
    num.LIM = 1 << 14; engine.BIGC = 60
    engine.memo.clear()
    try:
        r = engine.R(s, top=True)
    except (rules.Unknown, RuntimeError) as e:
        skip += 1; num.LIM = 1 << 62; engine.BIGC = 1000; continue
    num.LIM = 1 << 62; engine.BIGC = 1000
    a = [v.r if is_huge(v) else v % M for v in r]
    b = [v % M for v in t]
    if a == b and [is_huge(v) for v in r] == [v >= (1 << 14) for v in t]: agree += 1
    else:
        dis += 1
        if dis < 5: print('DIS', s, '\n  eng', r, '\n  exact', [v if v < 10**6 else 'big%d' % (v % M) for v in t])
print('agree', agree, 'disagree', dis, 'skip', skip, engine.stats, 'time %.0f' % (time.time() - t0))
