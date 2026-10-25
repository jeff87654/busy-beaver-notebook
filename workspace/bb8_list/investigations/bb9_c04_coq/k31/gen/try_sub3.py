import sys, time
from common import *
from d0spec import *
import mexp
# SUB c=4: L = 5j+4 -> D0(frz, 6, j+2, P-6, 3j-10, t+3); take j = J+12: L = 5J+64, L' = 3J+26, y' = J+14
J0 = 12
S = D0(1, 's', 0, 'y', 6, 'P', [run((1,) * 5, J=1)] + [1] * (5 * J0 + 4))
# frozen: 1 (10)^s 1 (10)^y  nearest-first: (01)^y 1 (01)^s, then the D0 '1' before l -- mid holds (01)^y 1 (01)^s
mid = [run((0, 1), y=1), 1, run((0, 1), s=1)]
Tg = D0(7, None, J0 + 2, 'J', 0, 'P', [run((1,) * 3, J=1)] + [1] * (3 * J0 - 10), tcon=3, mid=None,
        far=None)
# rebuild target left with mid: D0 part + mid + '1' + l : D0() puts [1] + far after mid; we need l-part = 1 (10)^s 1 (10)^y = nearest-first (01)^y 1 (01)^s 1
Tg = ('B', Tg[1][:-2] + [1] + [run((0, 1), y=1), 1, run((0, 1), s=1), 1, V('l')], [BLANK], '>')
print(pl.show(S)); print(pl.show(Tg))
t0 = time.time()
tree = mexp.explore(S, Tg, splits=2)
print('OK %.1fs' % (time.time() - t0))
print('\n'.join(mexp.describe(tree))[:6000])
