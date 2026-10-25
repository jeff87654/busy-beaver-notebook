import sys
from lib import *
def D(n): return '1' + '01' * n
P = [2, 1, 1, 0, 2, 1, 0, 1]
def cfg(X, Z, n, a):
    toks = P + [X] + [1] * Z + [0, 2] + [1] * n + [0, 3 * a + 1]
    return ''.join(D(t) for t in toks)
X, Z, n, a, N = map(int, sys.argv[1:6])
L = cfg(X, Z, n, a)
snaps, end = run(M10, L, 'G', '0', N, ['snap=G0'])
prev = None
for s in snaps:
    t = tokens(s[1])
    key = tuple(t[:-3])
    if key != prev:
        print(s[0], ctok(t))
        prev = key
print('END', end[0], end[1], ctok(tokens(end[2])), '|', end[3], '|', end[4][:80])
