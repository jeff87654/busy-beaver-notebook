from lib import *
import random, time
random.seed(1)
bad = 0; cnt = 0; t0 = time.time()
for trial in range(400):
    pre = [random.choice([1, 2, 3, 4, 5, 6, 7, 9]) for _ in range(random.randint(0, 3))]
    x = random.randint(4, 14)
    k = random.randint(0, 3)
    y = random.randint(2, 14)
    toks = [2] + pre + [x] + [1] * k + [0, y]
    bf, end = bforms(M10, toks, 2 * 10**6, maxsnap=2)
    t = bf[1][1] if len(bf) > 1 else None
    if k == 0:
        exp = [2] + pre + [x - 3, 0, 2 * y + 8]
    else:
        exp = [2] + pre + [x - 3, y + 3] + [1] * (k - 1) + [0, 4]
    cnt += 1
    if t != exp:
        bad += 1
        if bad < 10: print('MISMATCH', toks, '->', t, 'exp', exp, end[:2])
print('R1/R2 tests', cnt, 'mismatches', bad, 'time', time.time() - t0)
