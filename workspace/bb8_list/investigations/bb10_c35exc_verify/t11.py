from lib import *
from collections import Counter
def Estar(m, j):
    return '101011011011' + '011' * m, 'E', '0' + '111' + '01' * 7 + '00' + '101' * j + '101'
L, S, R = Estar(21, 3)
opts = ['snap=%s%d' % (s, b) for s in 'ABCDEFGHIJ' for b in (0, 1)]
snaps, end = run(M10, L, S, R, 3*10**6, opts)
print('right-edge', Counter(s[2] + s[3][0] for s in snaps))
opts = ['snapL=%s%d' % (s, b) for s in 'ABCDEFGHIJ' for b in (0, 1)]
snaps, end = run(M10, L, S, R, 3*10**6, opts)
print('left-edge', Counter(s[2] + s[3][0] for s in snaps))
