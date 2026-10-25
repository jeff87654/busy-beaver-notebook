from lib import *
from collections import Counter
opts = ['snap=%s%d' % (s, b) for s in 'ABCDEFGHIJ' for b in (0, 1)]
snaps, end = run(M10, '', 'A', '', 2000000, opts)
c = Counter(s[2] + s[3][0] for s in snaps)
print('right-edge', c)
opts = ['snapL=%s%d' % (s, b) for s in 'ABCDEFGHIJ' for b in (0, 1)]
snaps, end = run(M10, '', 'A', '', 2000000, opts)
c = Counter(s[2] + s[3][0] for s in snaps)
print('left-edge', c)
