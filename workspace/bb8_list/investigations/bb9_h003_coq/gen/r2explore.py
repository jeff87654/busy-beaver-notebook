"""Explore the r=2 halting branch symbolically: D0f t (75j+47) (20j+40+p) s y l  -> halt (target None)."""
import idle, sys, time
from common import *
from shapes import *
import mexp
from grp_sub import d0, U2, Y, S, L
START = d0(0, [run((1,) * 75, j=1)] + [1] * 47, [run((0, 0, 1), p=1), run((0, 0, 1) * 20, j=1)] + [0, 0, 1] * 40, Y, S, L)
t0 = time.time()
try:
    tree = mexp.explore(START, None, splits=int(sys.argv[1]) if len(sys.argv) > 1 else 0, maxstages=400)
    print('END', pl.show(tree.get('end')) if tree.get('end') else tree.keys())
except mexp.Fail as e:
    print('FAIL', str(e)[:3000])
print('%.0fs' % (time.time() - t0))
