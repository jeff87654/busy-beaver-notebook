"""from 11 D(x) D(m) (10)^r TAIL_j, run to next family config; print map"""
import sys
from tm import *
def tail(j): return '11' + '11111100' * j + '1001'
def nxt(w, t, mx=10**6):
    s = Sim(M11, w)
    s.step()
    while s.steps < mx:
        f = at_family(s, t)
        if f: return s.steps, f
        if not s.step(): return s.steps, 'HALT'
    return mx, None
j = int(sys.argv[1])
for x in (4,):
    for m in range(0, 6):
        for r in range(0, 9):
            w = '11' + D(x) + D(m) + '10' * r + tail(j)
            st, f = nxt(w, tail(j))
            print('m=%d r=%d ->' % (m, r), st, f)
