import lib
from lib import *
def D(n): return '1' + '01' * n
def B(a, ds):  # Ligocki B(a; d1..dn) ; ds nearest-first
    return ''.join(D(3 * d + 1) for d in reversed(ds)) + D(0) + D(3 * a + 1)
for a, k in [(0, 1), (1, 2), (2, 3), (5, 4)]:
    w = B(a, [0] * k)
    snaps, end = run(R8, w, 'G', '', 10**8, ['hist=G0'])
    print('R8 B(%d;0^%d)' % (a, k), end[0], end[1], 'ones', (end[2] + end[4]).count('1'), lib.last_hist)
    print('   final', rle(end[2]), '|', end[3], '|', rle(end[4]))
    snaps, end = run(R8, w, 'G', '', 10**8, ['snapany=G0'])
    print('   R8 G0 at', [(s[0], len(s[1])) for s in snaps][-5:])
