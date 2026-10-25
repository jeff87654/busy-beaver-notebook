"""Print the tape at each head-direction reversal (literal), for a start word."""
import sys
from tmlib import *
tm = {'main': MAIN, 'v1': VAR1, 'v2': VAR2}[sys.argv[1]]
w = expand(sys.argv[2]); maxsteps = int(sys.argv[3])
sim = Sim(tm, w, pad=200)
base = sim.pos
lastd = None
def line():
    t = sim.tape
    lo = base - 40; hi = base + len(w) + 40
    s = ''.join(str(c) for c in t[lo:sim.pos]) + '[' + ST[sim.state] + str(t[sim.pos]) + ']' + ''.join(str(c) for c in t[sim.pos+1:hi])
    return s
print('%6d %s' % (0, line()))
while sim.steps < maxsteps:
    p = sim.pos
    if not sim.step(): print('HALT'); break
    d = sim.pos - p
    if lastd is not None and d != lastd:
        print('%6d %s' % (sim.steps, line()))
    lastd = d
