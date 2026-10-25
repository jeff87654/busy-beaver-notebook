"""Waypoints of the used-up transient (n = 3, 11; r = 3c+5) for mexp, and literal checks of each leg."""
import sys, time, traceback
from common import *
from shapes import *
import mexp
U3 = (0, 1) * 3
U6 = (0, 1) * 6
P11 = [1, 1, BLANK]

def KP(acc, atok, rest):
    return ('B', tailpart() + acc + atok + rest + P11, [BLANK], '>')

def rside(segs):
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

def TOK(n):
    return '100' * (n + 2) + '101'

def Zc(n, xseg, kseg):
    return cfgL(['0'] + xseg + ['00'] + kseg + [TOK(n)])

def used(n):
    return KP(accr(5) + [run(U3, c=1)], tok(1), list(Z) * n)

def W1(n, order=0):
    xs = ['01' * 10, ('R', '01' * 6, 'c')] if order == 0 else [('R', '01' * 6, 'c'), '01' * 10]
    return Zc(n, xs, ['101'])

def ZS(n, order=0):
    return Zc(n, [('R', '01', 'x'), '01'] if order == 0 else ['01', ('R', '01', 'x')], [('R', '101', 'k')])

def ZT(n, order=0):
    return Zc(n, [('R', '01', 'x')], [('R', '101', 'k'), '101101'] if order == 0 else ['101101', ('R', '101', 'k')])

def Z0(n, order=0):
    return Zc(n, [], ['101' * 21, ('R', '101', 'm')] if order == 0 else [('R', '101', 'm'), '101' * 21])

def C1(n):
    """[3n+16, 1^(11+m), 2, 0, 3 | a = 3], r = 2"""
    return KP(accr(2), tok(3), tok(3) + tok(0) + tok(2) + list(Z) * 11 + [run(Z, m=1)] + tok(3 * n + 16))

def C1g():
    """generic: [.., 3+x, 1^(11+m), 2, 0, 3 | a = 3], r = 2   (context 1::l)"""
    return K(accr(2), tok(3), tok(3) + tok(0) + tok(2) + list(Z) * 11 + [run(Z, m=1)] + tok(3, 'x'))

def C2g():
    """[.., x, 21, 1^(9+m), 0, 0 | a = 19], r = 2"""
    return K(accr(2), tok(19), tok(0) + tok(0) + list(Z) * 9 + [run(Z, m=1)] + tok(21) + tok(0, 'x'))

def C3g():
    """[.., x, 21, 1^(7+m), 0, 1 | a = 762], r = 2"""
    return K(accr(2), tok(762), tok(1) + tok(0) + list(Z) * 7 + [run(Z, m=1)] + tok(21) + tok(0, 'x'))

def C2r():
    """[.., x, 21, 1^(9+m), 0, 0 | a = 1], r = 2+3q   (C2 after R1 x6)"""
    return K(accr(2, 'q', U3), tok(1), tok(0) + tok(0) + list(Z) * 9 + [run(Z, m=1)] + tok(21) + tok(0, 'x'))

def C3r():
    """[.., x, 21, 1^(7+m), 0, 1 | a = 2r+2], r = 2"""
    return K(accr(2), tok(6, 'q', U6), tok(1) + tok(0) + list(Z) * 7 + [run(Z, m=1)] + tok(21) + tok(0, 'x'))

def check(a, b, vals_list):
    for vals in vals_list:
        t0 = time.time()
        r = validate.reaches(a, b, vals, max_steps=3_000_000)
        print('  ', vals, '->', r, '%.1fs' % (time.time() - t0), flush=True)

def explore(name, a, b, pos=(), splits=6):
    pl.LEMMAS.clear()
    t0 = time.time()
    try:
        tree = mexp.explore(a, b, positive=frozenset(pos), splits=splits)
        print(name, 'OK %.1fs' % (time.time() - t0), flush=True)
        return tree
    except Exception as e:
        print(name, 'FAILED %.1fs' % (time.time() - t0), str(e)[:2000], flush=True)
        return None

if __name__ == '__main__':
    what = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    if what == 'check':
        print('UA', n); check(used(n), W1(n), [{'c': 0}, {'c': 1}, {'c': 2}])
        print('ZR', n); check(ZS(n), ZT(n), [{'x': 0, 'k': 1}, {'x': 3, 'k': 5}, {'x': 7, 'k': 2}])
        print('UB', n); check(Z0(n), C1(n), [{'m': 0}, {'m': 1}, {'m': 5}])
        print('C12'); check(C1g(), C2g(), [{'m': 0, 'x': 7}, {'m': 3, 'x': 19}])
        print('C23r'); check(C2r(), C3r(), [{'m': 0, 'x': 7, 'q': 0}, {'m': 3, 'x': 19, 'q': 2}, {'m': 1, 'x': 4, 'q': 126}])
    else:
        legs = {'UA': (used(n), W1(n)), 'UA2': (used(n), W1(n, 1)), 'ZR': (ZS(n), ZT(n)), 'ZR2': (ZS(n, 1), ZT(n, 1)),
                'UB': (Z0(n), C1(n)), 'UB2': (Z0(n, 1), C1(n)), 'C12': (C1g(), C2g()), 'C23': (C2r(), C3r())}
        a, b = legs[what]
        tree = explore(what, a, b)
        if tree and '-v' in sys.argv:
            print('\n'.join(mexp.describe(tree))[:6000])
