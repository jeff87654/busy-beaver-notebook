import sys
from lib import *
def D(n): return '1' + '01' * n
P = [2, 1, 1, 0, 2, 1, 0, 1]
def cfg(X, Z, n, a):
    toks = P + [X] + [1] * Z + [0, 2] + [1] * n + [0, 3 * a + 1]
    return ''.join(D(t) for t in toks)
for (X, Z, n, a) in [(3, 0, 1, 0), (3, 0, 1, 1), (3, 0, 2, 1), (9, 6, 2, 1), (9, 6, 3, 2), (15, 12, 2, 5)]:
    L = cfg(X, Z, n, a)
    snaps, end = run(M10, L, 'G', '0', 10**8, ['snap=G0', 'maxsnap=3'])
    print((X, Z, n, a), end[0], end[1])
    for s in snaps: print('   ', s[0], ctok(tokens(s[1])))
