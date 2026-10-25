import pickle
from common import *
from st0b import START as E0W     # E0 configuration with r = 5w + 3
D9 = tuple(tok(9))
def XA(v='v', j='j'):
    Lx = [0, 1] * 4 + list(Z) * 3 + [run(Z, i=1), run(Z * 8, **{j: 1})] + [1] + list(Z) * 19 + [run(Z * 20, **{v: 1})] \
         + tok(12) + [run(D9 * 4, **{j: 1}), BLANK]
    return ('F', Lx, [BLANK], '>')
