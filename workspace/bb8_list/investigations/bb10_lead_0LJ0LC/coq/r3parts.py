"""R3 (k+2 zero digits) split at waypoints found in literal traces.
W(j,i): left-to-right  l 1 (10)^(n+3) (110)^j 1 1 (10)^(B+3) 1  E>  1 (101)^i 0^inf
R(i,j): left-to-right  l 1 (10)^(n+1) 1 (10)^(B+4) (110)^i 1 1  G>  1 0 0 (101)^j 0^inf  """
import sys, time
from common import *
import mexp
P_n3 = [0, 1] * 3 + [run(U, n=1), 1, V('l')]
def W(j, i, jc=0, ic=0, P=None):
    left = [1] + [0, 1] * 3 + [run(U, B=1), 1, 1] + [0, 1, 1] * jc + ([run((0, 1, 1), **{j: 1})] if j else []) + (P if P is not None else P_n3)
    right = [1] + [1, 0, 1] * ic + ([run((1, 0, 1), **{i: 1})] if i else []) + [BLANK]
    return ('E', left, right, '>')
def R(i, j, ic=0, jc=0):
    left = [1, 1] + [0, 1, 1] * ic + ([run((0, 1, 1), **{i: 1})] if i else []) + [0, 1] * 4 + [run(U, B=1), 1, 0, 1, run(U, n=1), 1, V('l')]
    right = [1, 0, 0] + [1, 0, 1] * jc + ([run((1, 0, 1), **{j: 1})] if j else []) + [BLANK]
    return ('G', left, right, '>')
START = G(grp(0, B=1) + [run(Z, k=1)] + list(Z) * 2 + grp(3, n=1) + [1, V('l')])
TARGET = G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, B=1) + grp(1, n=1) + [1, V('l')])
PARTS = {
    'pre': (START, W('k', None, ic=1), ('B',)),
    'walk': (W('j', 'i', jc=1, P=[V('P')]), W('j', 'i', ic=1, P=[V('P')]), ('B',)),
    'borrow': (W(None, 'k', ic=1), R(None, 'k', jc=1), ('B',)),
    'ret': (R('i', 'j', jc=1), R('i', 'j', ic=1), ('B',)),
    'end': (R('k', None, ic=1), TARGET, ('B',)),
}
if __name__ == '__main__':
    for name in sys.argv[1].split(','):
        s, t, pos = PARTS[name]
        print(name, pl.show(s)); print('   ->', pl.show(t))
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
            print('  OK (%.1fs)' % (time.time() - t0))
            if '-v' in sys.argv: print('\n'.join(mexp.describe(tree)))
        except Exception as e:
            print('  FAIL', str(e)[:400])
