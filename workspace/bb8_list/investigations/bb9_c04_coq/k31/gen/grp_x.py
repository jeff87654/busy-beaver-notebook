"""Group 'x': key-31 local rules X1, X3, X4 and the halt H0 (target = the explored halting config), from try_x.py."""
import pickle
ITEMS = []
for nm in ('X1', 'X3', 'X4', 'H0'):
    S, T, tree = pickle.load(open('tree_x_%s.pkl' % nm, 'rb'))
    if T is None:
        T = tree['end']
    ITEMS.append((nm, S, T, dict(splits=0, maxstages=400), ()))
