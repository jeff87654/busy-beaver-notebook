"""val_small.py: for each residue c and small j, does the generic rule hold (several random contexts)?"""
import random, sys
from lit import *
import val_rules as V
rnd = random.Random(5)
res = {}
for c in (1, 2, 3, 4, 5):
    for j in range(2, 14):
        good = True
        for _ in range(3):
            l = V.far(); s = rnd.randint(1, 30); y = rnd.randint(1, 60); P = rnd.randint(80, 200); t = rnd.randint(0, 5)
            S = D0(l, s, y, P, 5 * j + c, t)
            if c == 1:
                if j < 6: good = False; break
                Tg = V.stop_target(l, s, y, P, j, t)
            else:
                ex, s2, yf, Lf, dP = V.SUB[c]
                if yf(j) < 0 or Lf(j) < 0: good = False; break
                Tg = D0(V.frz(l, s, y) + ex, s2, yf(j), P - dP, Lf(j), t + 3)
            r, out = check(S, Tg, steps=5 * 10**7)
            good &= r
        res[(c, j)] = good
    print('c=%d:' % c, ' '.join('%d%s' % (j, '+' if res[(c, j)] else '-') for j in range(2, 14)), flush=True)
