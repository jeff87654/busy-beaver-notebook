import sys, time
from common import *
from shapes import *
import mexp
from mexp import show
U6 = (0, 1) * 6
START = ('B', tailpart() + accr(2) + [run((0,1,0,1,0,1), b=1)] + tok(1) + [run(Z, n=1)] + [1, 1, BLANK], [BLANK], '>')
M2 = ('B', [run((1,0,0), n=1)] + [1,0,0]*3 + [1,1,1] + [0] + [0,1]*4 + [run(U6, b=1)] + [BLANK], [BLANK], '>')
if __name__ == '__main__':
    pl.LEMMAS.clear()
    t0=time.time()
    try:
        tree = mexp.explore(START, M2, positive=frozenset(sys.argv[1].split(',')) if len(sys.argv)>1 and sys.argv[1]!='-' else frozenset())
        print('explore OK %.1fs'%(time.time()-t0))
        print('\n'.join(mexp.describe(tree))[:3000])
    except Exception as e:
        print('FAILED', repr(e)[:500])
