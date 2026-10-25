import pickle, sys, time
from common import *
import mexp
from st2 import S2
S2P = engine.subst(S2, 'r', (('r', 1),), 11)            # r := r + 11  (2r - 18 = 2r' + 4)
T2 = KF(tok(1), tok(0), [run(Z, m=1)] + list(Z) * 41 + tok(3) + tok(4, 'r', (1, 0, 1, 0)) + tok(8) + [V('l')])
if __name__ == '__main__':
    t0 = time.time()
    try:
        tree = mexp.explore(S2P, T2, splits=0)
        print('stage 2 ok %.1fs' % (time.time() - t0))
        pickle.dump(tree, open('st2_tree.pkl', 'wb'))
    except mexp.Fail as e:
        print('FAIL', str(e)[:600])
