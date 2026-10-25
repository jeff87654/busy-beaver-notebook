import pickle, sys, time
from st0 import *
W0 = pickle.load(open('W0.pkl', 'rb'))
pre = int(sys.argv[1])
q, L, R, mode = merge_zeros(W0)
W1 = (q, [1, 0, 1] * pre + L, R, mode)
T = K([zeros(Z=1), tok(1) * (15 + pre), tok(5), tok(0), tok(2), tok(2), [run(tuple(tok(6)) * 4, b=1)], tok(6) * 2, [BLANK]], tok(1), tok(1))
t0 = time.time()
try:
    tree = mexp.explore(W1, T, positive=frozenset(['Z', 'b']), maxstages=600)
    print('OK %.1fs' % (time.time() - t0))
except Exception as e:
    print('FAIL', str(e)[:500])
