"""final special Si in the real w-class (w = 118 mod 120): halting and ones vs (Y, A, w), both size orders."""
import random
from fractions import Fraction as F
from fw import *
srv = Server(M10, 'Bf', 1)
rng = random.Random(4)
Q = [9, 9, 9, 2, 7, 0, 0, 3, 3, 0, 3, 0, 3, 0, 3, 0]
rows = []
for t in range(30):
    Y = 40 + 120 * rng.randint(0, 30) + 3; A = 40 + 120 * rng.randint(0, 30); w = 118 + 120 * rng.randint(0, 2)
    L = Q + [2, 1, 1, Y, 1, 0, 1, 2] + [1] * w
    wd, h, q = bword(L, A)
    x = srv.job(wd, h, q, 10 ** 12)[-1]
    base = sum(t + 1 for t in Q)  # ones of the prefix tokens (each D(m) has m+1 ones)
    rows.append((Y, A, w, x['kind'], x.get('ones')))
    print(Y, A, w, x['kind'], x.get('q'), x.get('c'), x.get('ones'), flush=True)
srv.close()
