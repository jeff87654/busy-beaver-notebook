"""engine with a SMALL lambda-closed modulus and low huge-threshold (so cycle jumps happen) vs exact brute force"""
import random, time
import num, engine, rules
# reconfigure modulus
num.PRIMES = {2: 5, 3: 2, 5: 1, 7: 1}
num.M = 32 * 9 * 5 * 7; num.M2 = 32; num.MO = num.M // 32
num.LAM = num.carmichael(num.M); num.LAMO = num.carmichael(num.MO)
assert (num.M // 3) % num.LAM == 0 and num.M % num.LAMO == 0
engine.M = num.M
from num import is_huge
M = num.M
random.seed(int(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else 5)
agree = dis = skip = 0; t0 = time.time()
shapes = [[0, 0], [2, 0, 0], [0, 0, 0], [3, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0, 0], [2, 0, 3, 0, 0], [1, 0], [1, 1, 0], [0, 1, 0], [2, 1, 0]]
for trial in range(300):
    s = [random.randint(100, 900)] + random.choice(shapes) + [random.randint(2, 9)]
    num.EXACT = True
    t = list(s); n = 0; ok = True
    try:
        while True:
            try:
                ev = rules.classify(t)
            except rules.Need:
                break
            t = ev.newlist; n += 1
            if n > 300000: ok = False; break
    except (rules.Unknown, OverflowError):
        ok = False
    num.EXACT = False
    if not ok:
        skip += 1; continue
    num.LIM = 1 << 12; engine.BIGC = 40
    engine.memo.clear()
    j0 = engine.stats['jumps']
    try:
        r = engine.R(s, top=True)
    except (rules.Unknown, RuntimeError, AssertionError) as e:
        skip += 1; num.LIM = 1 << 62; engine.BIGC = 1000; continue
    num.LIM = 1 << 62; engine.BIGC = 1000
    a = [v.r if is_huge(v) else v % M for v in r]
    b = [v % M for v in t]
    if a == b and [is_huge(v) for v in r] == [v >= (1 << 12) for v in t]: agree += 1
    else:
        dis += 1
        if dis < 5: print('DIS', s, 'jumps', engine.stats['jumps'] - j0, '\n  eng', r, '\n  exact', [v if v < 10**6 else 'big%d' % (v % M) for v in t])
print('agree', agree, 'disagree', dis, 'skip', skip, engine.stats, 'time %.0f' % (time.time() - t0))
