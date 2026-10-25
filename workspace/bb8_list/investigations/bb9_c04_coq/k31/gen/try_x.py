"""try_x.py NAME [FREE]: key-31 local rules (report sec. 3), free far side l unless FREE=0.
  X1: Kx (1^(n+2)) 1 (3R+2) t (0>>0>> lftx [2; w+1] l)          -->+ Kx (1^n ++ [6R+10; w]) 1 2 t l
  X3: Kx (1^(n+1) ++ [0]) 1 (3R+2) t (0>>0>> lftx [2; w+2] l)   -->+ Kx (1^n ++ [6R+10; w]) 1 2 t l
  X4: Kx (1^(n+1) ++ [0]) 1 (3R+2) t (0>>0>> lftx [2;0] (0>>0>> lftx [W; 2] l)) -->+ Kx (1^n ++ [6R+W+11; 1]) 1 2 t l
  H0: Kx (1^n ++ [0; d+1; s]) 1 (3R+2) t l  -->+  halt (H reading 1)
Saves tree_x_NAME.pkl."""
import sys, time, pickle
from common import *
from shapes import tok, Z, accr
import mexp
NAME = sys.argv[1]; FREE = int(sys.argv[2]) if len(sys.argv) > 2 else 1
FAR = [V('l')] if FREE else [1, V('l')]
R6 = (0, 1) * 6


def KX(acc, zeros, rest):
    tail = [1, 0, 0, 1] + [run(TB, t=1), 1, 1]
    return ('B', tail + acc + tok(1) + zeros + rest + FAR, [BLANK], '>')


def zr(c, var):
    return [run((1, 0, 1), **{var: 1})] + [1, 0, 1] * c


A = accr(2, 'R', (0, 1) * 3)
if NAME == 'X1':
    S = KX(A, zr(2, 'n'), [0, 0] + tok(2) + tok(1, 'w'))
    T = KX(accr(2), zr(0, 'n'), tok(10, 'R', R6) + tok(0, 'w'))
elif NAME == 'X3':
    S = KX(A, zr(1, 'n'), tok(0) + [0, 0] + tok(2) + tok(2, 'w'))
    T = KX(accr(2), zr(0, 'n'), tok(10, 'R', R6) + tok(0, 'w'))
elif NAME == 'X4':
    S = KX(A, zr(1, 'n'), tok(0) + [0, 0] + tok(2) + tok(0) + [0, 0] + tok(0, 'W') + tok(2))
    T = KX(accr(2), zr(0, 'n'), [1] + [0, 1] * 11 + [run(R6, R=1), run((0, 1), W=1)] + tok(1))
elif NAME == 'H0':
    S = KX(A, zr(0, 'n'), tok(0) + tok(1, 'd') + tok(0, 's'))
    T = None
if __name__ == '__main__':
    print('S', pl.show(S)[:200]); print('T', pl.show(T)[:200] if T else None)
    t0 = time.time()
    pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
    tree = mexp.explore(S, T, splits=0 if T else 0, maxstages=400)
    if T is None:
        print('END', pl.show(tree['end']))
    print('OK %.1fs' % (time.time() - t0))
    pickle.dump((S, T, tree), open('tree_x_%s.pkl' % NAME, 'wb'))
