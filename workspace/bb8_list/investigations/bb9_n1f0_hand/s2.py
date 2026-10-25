import sys
from c7lib import *
M, bo, c, maxs, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
w = J(bo, 0, [0,0,0], 0, c)
print(tr(M, w, maxs, 'dshape', n))
