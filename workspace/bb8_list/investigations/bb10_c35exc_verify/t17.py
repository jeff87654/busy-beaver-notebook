import sys
from lib import *
P = [2, 1, 1, 0, 2, 1, 0, 1]
X, Z, n, a, N = map(int, sys.argv[1:6])
toks = P + [X] + [1] * Z + [0, 2] + [1] * n + [0, 3 * a + 1]
ms, end = macro_steps(M10, toks, N)
for (s1, t1), (s2, t2) in zip(ms, ms[1:]):
    k, a1, a2 = diff(t1, t2)
    if len(a1) == 2 and len(a2) == 2 and a2[0] == a1[0] - 1 and a2[1] == a1[1] + 2:
        continue  # plain round
    print(s1, 'depth', len(t1) - k, ctok(a1), '->', ctok(a2), '  steps', s2 - s1)
print('END', end[0], end[1])
