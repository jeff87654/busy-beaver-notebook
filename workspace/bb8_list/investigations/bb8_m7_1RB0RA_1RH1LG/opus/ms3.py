"""Pieces of the used-up transient (13 tokens D(1), r = 3b+2) for mexp."""
import sys, time, traceback
from ms import *

def rside(segs):
    """right side, segments left to right (nearest first)."""
    out = []
    for seg in segs:
        if isinstance(seg, str):
            out += [int(ch) for ch in seg]
        else:
            _, block, var = seg
            cnt = var if isinstance(var, dict) else {var: 1}
            out.append(run(tuple(int(ch) for ch in block), **cnt))
    return out

def cfgL(rsegs):
    """head in B on the leftmost cell of the word (blank left of it)."""
    return ('B', [BLANK], rside(rsegs) + [BLANK], '>')

TOK = '100' * 13 + '101'
def Zc(xseg, kseg):
    return cfgL(['0'] + xseg + ['00'] + kseg + [TOK])

ZB = Zc(['01' * 4, ('R', '01' * 6, 'b')], ['101'])          # Z(6b+4, 1)
ZB2 = Zc([('R', '01' * 6, 'b'), '01' * 4], ['101'])         # same, other order
ZS = Zc([('R', '01', 'x'), '01'], [('R', '101', 'k')])      # Z(S x, k)
ZS2 = Zc(['01', ('R', '01', 'x')], [('R', '101', 'k')])
ZT = Zc([('R', '01', 'x')], [('R', '101', 'k'), '101101'])  # Z(x, S (S k))
ZT2 = Zc([('R', '01', 'x')], ['101101', ('R', '101', 'k')])
Z0 = Zc([], ['101', ('R', '101', 'k')])                     # Z(0, S k)
M3k = cfgB(['1010', '111', ('R', '001', 'k'), '1' * 39, '001001'])
M4k = cfgB(['1010', '111', ('R', '001', 'k'), '0', '1111', '000111' * 5, '00110', '111111', '001001'])
Z09 = Zc([], ['101' * 9, ('R', '101', 'k')])                # Z(0, k + 9)
M3k8 = cfgB(['1010', '111', ('R', '001', 'k'), '001' * 8, '1' * 39, '001001'])
M4k8 = cfgB(['1010', '111', ('R', '001', 'k'), '001' * 7, '0', '1111', '000111' * 5, '00110', '111111', '001001'])
M3k1 = cfgB(['1010', '111', ('R', '001', 'k'), '001', '1' * 39, '001001'])
M4k1 = cfgB(['1010', '111', ('R', '001', 'k'), '0', '1111', '000111' * 5, '00110', '111111', '001001'])
Z02 = Zc([], ['101101', ('R', '101', 'k')])                 # Z(0, k + 2)
P = {'Z02': Z02, 'Z09': Z09, 'M3k8': M3k8, 'M4k8': M4k8, 'M3k1': M3k1, 'M4k1': M4k1, 'M0': M0, 'Y0': Y0, 'M2': M2, 'ZB': ZB, 'ZB2': ZB2, 'ZS': ZS, 'ZS2': ZS2, 'ZT': ZT, 'ZT2': ZT2, 'Z0': Z0, 'M3k': M3k, 'M4k': M4k}

if __name__ == '__main__':
    a, b = sys.argv[1], sys.argv[2]
    splits = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    pl.LEMMAS.clear()
    t0 = time.time()
    try:
        tree = mexp.explore(P[a], P[b], splits=splits)
        print(a, '->', b, 'OK %.1fs' % (time.time() - t0))
        if '-v' in sys.argv:
            print('\n'.join(mexp.describe(tree))[:6000])
    except Exception as e:
        print(a, '->', b, 'FAILED %.1fs' % (time.time() - t0), str(e)[:1500])
