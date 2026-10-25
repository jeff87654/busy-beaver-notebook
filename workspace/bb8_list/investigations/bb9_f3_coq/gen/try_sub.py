"""python try_sub.py C E [PB] : explore SUB for L = 5j+C (C in 2,3,4,5), parked P = PB*p + E + PBASE (concrete part first)."""
import sys, time
from common import *
import d0spec
from d0spec import *
import mexp
C = int(sys.argv[1]); E = int(sys.argv[2]); d0spec.PB = int(sys.argv[3]) if len(sys.argv) > 3 else 6; d0spec.KL = int(sys.argv[4]) if len(sys.argv) > 4 else 6
SUB = {2: (4, 5, -4, 3, 8, 11), 3: (None, 2, 1, 3, -7, 4), 4: (None, 6, 2, 3, -10, 6), 5: (None, 4, 3, 3, -7, 6)}
ex, s2, ya, la, lb, dP = SUB[C]
J0 = {2: 8, 3: 3, 4: 4, 5: 3}[C]
PBASE = {2: 18, 3: 12, 4: 12, 5: 12}[C]
S = D0(1, 's', 0, 'y', E + PBASE, 'p', [run((1,) * 5, J=1)] + [1] * (5 * J0 + C))
Lt = la * J0 + lb
Tg = D0(s2 + 1, None, J0 + ya, 'J', E + PBASE - dP, 'p', [run((1,) * 3, J=1)] + [1] * Lt, tcon=3)
mid = [run((0, 1), y=1), 1, run((0, 1), s=1), 1]
if ex: mid = [0, 1] * ex + [1] + mid       # nearest-first: (01)^4 then its closing 1 ... frozen
Tg = ('B', Tg[1][:-2] + [1] + mid + [V('l')], [BLANK], '>')
print(pl.show(S)); print(pl.show(Tg))
t0 = time.time()
tree = mexp.explore(S, Tg, splits=0)
print('OK %.1fs' % (time.time() - t0))
import pickle; pickle.dump((S, Tg, tree), open('tree_sub_%d_%d.pkl' % (C, E), 'wb'))
print('\n'.join(mexp.describe(tree))[:3000])
