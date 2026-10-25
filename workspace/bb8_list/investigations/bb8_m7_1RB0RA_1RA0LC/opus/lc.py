"""Lifecycle configurations (K-form, P11 left end) for mexp.  b = S c throughout (r = 3c+5)."""
import sys, time, traceback
from common import *
from shapes import *
import mexp
U3 = (0, 1, 0, 1, 0, 1)
U6 = (0, 1) * 6
P11 = [1, 1, BLANK]

def KP(acc, atok, rest):
    return ('B', tailpart() + acc + atok + rest + P11, [BLANK], '>')

def used(n):
    """K0(1^(n+1)), r = 3c+5"""
    return KP(accr(5) + [run(U3, c=1)], tok(1), list(Z) * n)

def C1(n):
    """[T+3, 1^(12c+11), 2, 0, 3, 3] r = 2"""
    T = 3 * n + 13
    return KP(accr(2), tok(3), tok(3) + tok(0) + tok(2) + list(Z) * 11 + [run(Z * 12, c=1)] + tok(T + 3))

def tryit(a, b, splits=6, verbose=False):
    pl.LEMMAS.clear()
    t0 = time.time()
    try:
        tree = mexp.explore(a, b, splits=splits)
        print('OK %.1fs' % (time.time() - t0), flush=True)
        if verbose:
            print('\n'.join(mexp.describe(tree))[:8000])
        return tree
    except Exception as e:
        print('FAILED %.1fs' % (time.time() - t0), str(e)[:3000], flush=True)
        return None

if __name__ == '__main__':
    n = int(sys.argv[1])
    tryit(used(n), C1(n), verbose='-v' in sys.argv)
