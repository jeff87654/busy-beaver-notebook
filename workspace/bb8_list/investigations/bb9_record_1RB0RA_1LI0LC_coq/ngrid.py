"""exhausted blank-left config 11 D1^n D1(a) (10)^r tail(j) -> first family config / halt.  python ngrid.py NMAX RLIST J MAXSTEPS"""
import sys
from tm import *
from tprobe import word, tail
nmax = int(sys.argv[1]); rs = [int(x) for x in sys.argv[2].split(',')]; j = int(sys.argv[3]); mx = int(sys.argv[4])
for n in range(nmax + 1):
    for r in rs:
        s = Sim(M11, word([1] * (n + 1), r, j))
        s.step()
        res = None
        while s.steps < mx:
            f = at_family_any(s)
            if f:
                ms, rr, jj = f
                res = '%d: %s r=%d j=%d' % (s.steps, ms if len(ms) < 12 else str(ms[:8]) + '..(%d)..' % len(ms) + str(ms[-3:]), rr, jj); break
            if not s.step():
                res = 'HALT %d ones %d' % (s.steps, sum(s.t)); break
        print('n=%d r=%d -> %s' % (n, r, res), flush=True)
