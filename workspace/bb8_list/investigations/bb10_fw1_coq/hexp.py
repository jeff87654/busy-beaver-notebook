import sys, time, pickle
from parts import *
c = int(sys.argv[1]); prew = int(sys.argv[2]) if len(sys.argv) > 2 else 1
S = W2(dict(w=1), None, dict(k=1), pre_w=prew, beyond=[1, V('l')], extra_zeros=c, zblk=5)
t0 = time.time()
try:
    tree = mexp.explore(S, None, positive=frozenset(['w', 'k']))
    print('c=%d OK halt (%.1fs)' % (c, time.time() - t0))
    print('\n'.join(mexp.describe(tree))[-3000:])
except Exception as e:
    print('c=%d FAIL' % c, str(e)[:600])
