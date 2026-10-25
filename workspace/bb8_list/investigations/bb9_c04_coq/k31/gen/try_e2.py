"""try_e2.py RHO [FREE]: key-31 post-ESC exhaustion E2 (report sec. 2), K = 5w + 15 + RHO (u = w + 3):
  Kx (1^K ++ [2;6;2]) 1 (3R+2) t e  -->+  (t+3)-form by RHO:
   0: Kx (1^(3w+3) ++ [6R+3w+21; 1; 2]) 1 2 (t+3) e
   1: Kx (1^(3w+2) ++ [3w+10]) 1 2 (t+3) (0>>0>> lftx [2; 6R+8; 3; 2] e)
   2: Kx (1^(3w+6) ++ [3w+15; 6R+1; 4; 2]) 1 2 (t+3) e
   3: Kx (1^(3w+4) ++ [3w+12]) 1 2 (t+3) (0>>0>> lftx [2; 6R+6; 3; 2] e)
   4: Kx (1^(3w+4) ++ [3w+12]) 1 2 (t+3) (0>>0>> lftx [2;0] (0>>0>> lftx [6R+7; 2; 2] e))
  e = the far side beyond the token 2 (free l, or 1 >> l when FREE=0).  Saves tree_e2_RHO.pkl."""
import sys, time, pickle
from common import *
from shapes import tok, Z, tailpart, accr
import mexp
RHO = int(sys.argv[1]); FREE = int(sys.argv[2]) if len(sys.argv) > 2 else 1
FAR = [V('l')] if FREE else [1, V('l')]


def toks(*ts):
    out = []
    for t in ts:
        if isinstance(t, tuple):        # (const, var, blk)
            out += tok(t[0], t[1], t[2])
        elif t == 'z2':
            out += [0, 0]
        else:
            out += tok(t)
    return out


def KX(tcon, acc, zeros, rest):
    tail = [1, 0, 0, 1] + list(TB) * tcon + [run(TB, t=1), 1, 1]
    return ('B', tail + acc + tok(1) + zeros + rest + FAR, [BLANK], '>')


def zr(c, var, k):
    return [run((1, 0, 1) * k, **{var: 1})] + [1, 0, 1] * c


R6 = (0, 1) * 6
S = KX(0, accr(2, 'R', (0, 1) * 3), zr(15 + RHO, 'w', 5), toks(2, 6, 2))
W3 = (0, 1) * 3
if RHO == 0:
    T = KX(3, accr(2), zr(3, 'w', 3), [1] + [0, 1] * 21 + [run(W3, w=1), run(R6, R=1)] + toks(1, 2))
elif RHO == 1:
    T = KX(3, accr(2), zr(2, 'w', 3), [1] + [0, 1] * 10 + [run(W3, w=1)] + toks('z2', 2, (8, 'R', R6), 3, 2))
elif RHO == 2:
    T = KX(3, accr(2), zr(6, 'w', 3), [1] + [0, 1] * 15 + [run(W3, w=1)] + toks((1, 'R', R6), 4, 2))
elif RHO == 3:
    T = KX(3, accr(2), zr(4, 'w', 3), [1] + [0, 1] * 12 + [run(W3, w=1)] + toks('z2', 2, (6, 'R', R6), 3, 2))
else:
    T = KX(3, accr(2), zr(4, 'w', 3), [1] + [0, 1] * 12 + [run(W3, w=1)] + toks('z2', 2, 0, 'z2', (7, 'R', R6), 2, 2))
if __name__ == '__main__':
    print('S', pl.show(S)[:200]); print('T', pl.show(T)[:200])
    t0 = time.time()
    pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
    tree = mexp.explore(S, T, splits=0, maxstages=400)
    print('OK %.1fs' % (time.time() - t0))
    pickle.dump((S, T, tree), open('tree_e2_%d.pkl' % RHO, 'wb'))
