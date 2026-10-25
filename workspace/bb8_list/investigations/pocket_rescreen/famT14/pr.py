import sys
from drv import *
M = T2 if '-2' in sys.argv else T1
for s in sys.argv[1:]:
    if s == '-2': continue
    ds, b = s.rsplit(':', 1)
    print('%-30s b=%-4s -> %s' % (ds, b, p1(ds, 0, int(b), M)))
