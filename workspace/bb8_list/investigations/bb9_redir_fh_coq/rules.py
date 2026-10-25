import sys, time
from common import *
import mexp
ITEMS = [
    ('R1', KF(tok(3, 'm'), tok(0, 'r'), [V('l')]), KF(tok(0, 'm'), tok(6, 'r', (1, 0, 1, 0)), [V('l')]), ()),
    ('R2', KF(tok(1), tok(0, 'r'), tok(3, 'x') + [V('l')]), KF(tok(7, 'r', (1, 0, 1, 0)), tok(0), tok(0, 'x') + [V('l')]), ()),
    ('R3', KF(tok(1), tok(0, 'r'), list(Z) + [run(Z, k=1)] + tok(3, 'x') + [V('l')]),
           KF(tok(1), tok(0), [run(Z, k=1)] + tok(7, 'r', (1, 0, 1, 0)) + tok(0, 'x') + [V('l')]), ()),
]
if __name__ == '__main__':
    for name, s, t, pos in ITEMS:
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos), splits=2)
            print(name, 'ok %.1fs' % (time.time() - t0))
            print('\n'.join(mexp.describe(tree))[:1500])
        except mexp.Fail as e:
            print(name, 'FAIL', str(e)[:800])
