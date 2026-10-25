import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
from fwmin import *
import xcheck
code, es, er, w, d, x = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
out = sys.argv[7]; steps = int(sys.argv[8]) if len(sys.argv) > 8 else 2000000
z = build(boot=(code, es, er, (w, d, x)))
f, dd, t, fw = emit(z, out)
print('framework', f, 'DAG', dd, 'total', t)
print(xcheck.crosscheck(out, steps))
print(xcheck.compare_tapes(out, 30))
