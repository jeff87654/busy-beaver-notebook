"""D2 stage: P + [2] + 1^k + a=1, r, j -> first family config / halt.  python kgrid.py "P" KMIN KMAX RLIST J MAXSTEPS"""
import sys
from tm import *
from tprobe import word, tail
P = [int(x) for x in sys.argv[1].split(',')] if sys.argv[1] else []
k0, k1 = int(sys.argv[2]), int(sys.argv[3]); rs = [int(x) for x in sys.argv[4].split(',')]; j = int(sys.argv[5]); mx = int(sys.argv[6])
for k in range(k0, k1 + 1):
    for r in rs:
        s = Sim(M11, word(P + [2] + [1] * (k + 1), r, j))
        s.step()
        res = None
        while s.steps < mx:
            f = at_family_any(s)
            if f:
                ms, rr, jj = f
                res = '%d: %s r=%d j=%d' % (s.steps, ms if len(ms) < 14 else str(ms[:10]) + '..(%d)..' % len(ms) + str(ms[-3:]), rr, jj); break
            if not s.step():
                res = 'HALT %d ones %d' % (s.steps, sum(s.t)); break
        print('k=%d r=%d -> %s' % (k, r, res), flush=True)
