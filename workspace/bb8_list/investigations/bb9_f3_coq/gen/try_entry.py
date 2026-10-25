"""python try_entry.py E : explore ENTRY Kt(ctx D(a+4) D1^P D0 D2 z2 D1^(N+2); 1; 3R+2; t) -> D0(l, a+1, 6R+9, P, 3N+2, t+1)."""
import sys, time, pickle
from common import *
import d0spec
from d0spec import *
import mexp
E = int(sys.argv[1]); PBASE = 12
D1 = (1, 0, 1)
def parked(blk):
    return list(blk) * (E + PBASE - 6) + [run(tuple(blk) * 6, p=1)] + list(blk) * 6
left = [1, 0, 0, 1, run(TB, t=1), 1, 1] + [0, 1, 0, 1, run((0, 1) * 3, R=1)] + [1, 0, 1]
left += [run(D1, N=1)] + list(D1) * 2 + [0, 0, 1, 0, 1, 0, 1, 1] + parked(D1)
left += [1] + [0, 1] * 4 + [run((0, 1), a=1)] + [1, V('l')]
S = ('B', left, [BLANK], '>')
tl = [1, 0, 0, 1] + list(TB) + [run(TB, t=1), 1, 1] + [run((1, 1, 1), N=1), 1, 1] + parked((0, 0, 1))
tl += [1, 1, 0] + [0, 1] * 9 + [run((0, 1) * 6, R=1)] + [1] + [0, 1] * 2 + [run((0, 1), a=1)] + [1, V('l')]
Tg = ('B', tl, [BLANK], '>')
print(pl.show(S)); print(pl.show(Tg))
t0 = time.time()
tree = mexp.explore(S, Tg, splits=0)
print('OK %.1fs' % (time.time() - t0))
pickle.dump((S, Tg, tree), open('tree_entry_%d.pkl' % E, 'wb'))
