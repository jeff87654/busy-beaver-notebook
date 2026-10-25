"""exact ones at the halt of the second unpack event, real classes; fit ones = a n + b Y + c T + d w + e A + f."""
import sys, itertools, random
from fractions import Fraction as F
from fw import *
srv = Server(M10, 'Bf', 1)
rows = []
specs = []
rng = random.Random(5)
for _ in range(int(sys.argv[1])):
    n = rng.choice([1, 2, 3, 5]); A = 40 + 120 * rng.randint(0, 3); w = 103 + 120 * rng.randint(0, 2)
    Y = 32 + 120 * rng.randint(0, 3); T = 40 * A + 481 + 120 * rng.randint(0, 6)
    specs.append((n, A, w, Y, T))
for n, A, w, Y, T in specs:
    L = [6] * n + [3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A)
    x = srv.job(wd, h, q, 10 ** 12)[-1]
    it, idx, off = tokpos(x['word'], x['rel'])
    rows.append((n, Y, T, w, A, x['ones'], x['kind'], len(it) - idx, x['step']))
    print(n, A, w, Y, T, x['kind'], x.get('ones'), len(it) - idx, x['step'], flush=True)
srv.close()


def solve(M, v):
    k = len(M); M = [list(map(F, r)) + [F(x)] for r, x in zip(M, v)]
    for i in range(k):
        p = next(r for r in range(i, k) if M[r][i] != 0); M[i], M[p] = M[p], M[i]
        for r in range(k):
            if r != i and M[r][i] != 0:
                f = M[r][i] / M[i][i]; M[r] = [a - f * b for a, b in zip(M[r], M[i])]
    return [M[i][k] / M[i][i] for i in range(k)]


X = [list(r[:5]) + [1] for r in rows]; y = [r[5] for r in rows]
for _ in range(500):
    idx = rng.sample(range(len(rows)), 6)
    try:
        c = solve([X[i] for i in idx], [y[i] for i in idx]); break
    except StopIteration:
        continue
print('ones = %s*n + %s*Y + %s*T + %s*w + %s*A + %s' % tuple(c))
print('mismatches', sum(1 for r, yy in zip(X, y) if sum(a * b for a, b in zip(c, r)) != yy), 'of', len(rows),
      ' all HALT:', all(r[6] == 'HALT' for r in rows), ' right=20:', all(r[7] == 20 for r in rows))
