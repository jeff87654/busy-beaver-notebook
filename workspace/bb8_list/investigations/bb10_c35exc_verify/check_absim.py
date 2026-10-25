"""check_absim.py -- compare absim.step against literal B-form events of sim.exe on random configurations"""
import random, sys, time
from lib import *
import absim
from collections import Counter
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
NT = int(sys.argv[2]) if len(sys.argv) > 2 else 300
P = [2, 1, 1, 0, 2, 1, 0, 1]
stats = Counter(); unk = Counter(); bad = 0; t0 = time.time()
for trial in range(NT):
    body = [random.choice([0, 1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 8, 9]) for _ in range(random.randint(1, 6))]
    toks = P + [random.randint(12, 30)] + body + [0, random.randint(2, 12)]
    bf, end = bforms(M10, toks, 3 * 10**6, maxsnap=8)
    t = list(toks)
    for (s, lit) in bf[1:]:
        try:
            t2, r = absim.step(t)
        except absim.Unknown as e:
            unk[str(e)] += 1
            break
        if t2 != lit:
            bad += 1
            if bad <= 15:
                print('MISMATCH rule', r, 'from', ctok(t), '\n   abs', ctok(t2), '\n   lit', ctok(lit))
            break
        stats[r] += 1
        t = t2
print('rules verified:', dict(stats))
print('unknown patterns:', dict(unk))
print('mismatches', bad, 'time %.1f' % (time.time() - t0))
