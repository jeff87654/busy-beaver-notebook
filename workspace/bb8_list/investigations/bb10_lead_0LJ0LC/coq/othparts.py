import sys, time
from common import *
import mexp
PARTS = {
  # halt: N(0, 0^(L+1) | B units) halts
  'halt': (G(grp(0, B=1) + [run(Z, L=1)] + list(Z) + [1, 1, BLANK]), None, ('B',)),
  # rebuild: C(0^(m+1) | B units) -> N(6, 0^(2B+m+5) | 1 unit)
  'rebuild': (G(grp(0, B=1) + [run(Z, m=1)] + list(Z) + [1, BLANK]),
              G(grp(1) + [run(Z, B=2, m=1)] + list(Z) * 5 + grp(6) + [1, BLANK]), ('B',)),
}
if __name__ == '__main__':
    for name in sys.argv[1].split(','):
        s, t, pos = PARTS[name]
        print(name, pl.show(s)); print('   ->', pl.show(t) if t else 'HALT')
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
            print('  OK (%.1fs)' % (time.time() - t0))
            if '-v' in sys.argv: print('\n'.join(mexp.describe(tree)))
        except Exception as e:
            print('  FAIL', str(e)[:600])
