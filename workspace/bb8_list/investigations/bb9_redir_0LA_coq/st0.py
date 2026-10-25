import sys, time
from common import *
from phases import *
import mexp
L0 = [0, 1, 1, 0, run((1, 1, 0) * 5, n=1), 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, BLANK]
R0 = [1, 1, 1, 0] + [1, 0] * 7 + [0, run(Z, J=1), 1, 0, 1, BLANK]
START = ('E', L0, R0, '<')
# Kr (1^(2n+J) ++ 7 :: 6 :: 8 :: 9^n) 1 0
TARGET = KR(tok(1), tok(1), [run(Z, J=1), run(Z * 2, n=1)] + tok(7) + tok(6) + tok(8) + [run(tuple(tok(9)), n=1), BLANK])
if __name__ == '__main__':
    t0 = time.time()
    tree = mexp.explore(START, TARGET, splits=2)
    print('\n'.join(mexp.describe(tree))[:6000])
    print('%.1fs' % (time.time() - t0))
