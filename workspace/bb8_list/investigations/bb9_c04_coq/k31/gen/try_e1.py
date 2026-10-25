"""try_e1.py E [PBASE]: key-31 entry  D0f t 32 P s y l -->+ Kx (1^K ++ [5;6;2;5;4;y;s]) 1 2 (t+9) (1 >> l),  K = P - 20,
parked P = 6p + E + PBASE (period-6 run, as in the SUB family).  Saves tree_e1_E.pkl."""
import sys, time, pickle
from common import *
import d0spec
from d0spec import D0
from shapes import tok, Z
import mexp
E = int(sys.argv[1]); PBASE = int(sys.argv[2]) if len(sys.argv) > 2 else 24
d0spec.PB = 6; d0spec.KL = 6
S = D0(1, 's', 0, 'y', E + PBASE, 'p', [1] * 32)
Kc = E + PBASE - 20
near = [run((1, 0, 1) * 6, p=1)] + [1, 0, 1] * Kc
rest = near + tok(5) + tok(6) + tok(2) + tok(5) + tok(4) + [1, run((0, 1), y=1)] + [1, run((0, 1), s=1)]
T = ('B', [1, 0, 0, 1] + list(TB) * 9 + [run(TB, t=1), 1, 1] + [0, 1, 0, 1] + [1, 0, 1] + rest + [1, V('l')], [BLANK], '>')
if __name__ == '__main__':
    print('S', pl.show(S)[:200]); print('T', pl.show(T)[:200])
    t0 = time.time()
    pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
    tree = mexp.explore(S, T, splits=0, maxstages=400)
    print('OK %.1fs' % (time.time() - t0))
    pickle.dump((S, T, tree), open('tree_e1_%d.pkl' % E, 'wb'))
