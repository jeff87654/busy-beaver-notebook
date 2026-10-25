"""python try_stop.py E : explore STOP (L = 5j+1, j = J+6), parked P = 6p + E + 12."""
import sys, time, pickle
from common import *
import d0spec
from d0spec import *
import mexp
E = int(sys.argv[1]); d0spec.PB = 6; d0spec.KL = 6
J0 = 6; PBASE = 12
S = D0(1, 's', 0, 'y', E + PBASE, 'p', [run((1,) * 5, J=1)] + [1] * (5 * J0 + 1))
D1 = (1, 0, 1)
nc = E + PBASE - 3 - 6
left = [1, 0, 0, 1] + list(TB) * 2 + [run(TB, t=1), 1, 1] + [0, 1, 0, 1] + [1, 0, 1] + [run(D1, J=1)]
left += [1] + [0, 1] * 8 + [run((0, 1), J=1)] + [0, 0] + [1, 0, 1, 0, 1] + [1]
left += list(D1) * nc + [run(D1 * 6, p=1)] + list(D1) * 6
left += [1] + [0, 1] * 3 + [run((0, 1), y=1)] + [1] + [run((0, 1), s=1)] + [1, V('l')]
Tg = ('B', left, [BLANK], '>')
print(pl.show(S)); print(pl.show(Tg))
t0 = time.time()
tree = mexp.explore(S, Tg, splits=0)
print('OK %.1fs' % (time.time() - t0))
pickle.dump((S, Tg, tree), open('tree_stop_%d.pkl' % E, 'wb'))
