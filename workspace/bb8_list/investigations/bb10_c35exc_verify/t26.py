import random, time
import engine, rules
from num import H, M, is_huge
from tower import tower_res
from lib import ctok
# 1) engine vs brute force on small exact suffixes (values stay exact)
random.seed(5)
agree = disagree = skipped = 0
for trial in range(3000):
    s = [random.choice([0, 1, 1, 2, 3, 4, 5, 6, 7, 9, 10]) for _ in range(random.randint(1, 4))] + [0, random.randint(2, 9)]
    # brute force
    t = list(s); ok = True; n = 0
    try:
        while True:
            try:
                ev = rules.classify(t)
            except rules.Need:
                break
            if ev.lo < 0: break
            t = ev.newlist; n += 1
            if any(is_huge(v) for v in t) or n > 5000:
                ok = False; break
    except rules.Unknown:
        ok = False
    if not ok:
        skipped += 1; continue
    engine.memo.clear()
    try:
        r = engine.R(s)
    except rules.Unknown:
        skipped += 1; continue
    if list(r) == t: agree += 1
    else:
        disagree += 1
        if disagree < 5: print('DIS', s, r, t)
print('engine vs brute: agree', agree, 'disagree', disagree, 'skipped', skipped)
# 2) the real inner game
T = tower_res(M)
A = H(3 * T - 6)
s = [A] + [1] * 36 + [0, 6]
engine.memo.clear()
t0 = time.time()
try:
    r = engine.R(s)
    print('INNER GAME RESULT:', ctok([str(v) for v in r]) if False else r)
except rules.Unknown as e:
    print('UNKNOWN pattern in inner game:', e)
print(engine.stats, 'time %.1f' % (time.time() - t0))
