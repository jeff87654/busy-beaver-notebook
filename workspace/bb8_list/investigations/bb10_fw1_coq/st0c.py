import pickle, sys, time
from st0 import *
W0 = pickle.load(open('W0.pkl', 'rb'))
W1 = merge_zeros(W0)
T = K([zeros(Z=1), tok(1) * 15, tok(5), tok(0), tok(2), tok(2), [run(tuple(tok(6)) * 4, b=1)], tok(6) * 2, [BLANK]], tok(1), tok(1))
print(pl.show(T))
t0 = time.time()
tree = mexp.explore(W1, T, positive=frozenset(['Z', 'b']))
print('OK %.1fs' % (time.time() - t0))
pickle.dump(tree, open('ST0b_tree.pkl', 'wb'))
