"""Group 'e2': key-31 post-ESC exhaustion E2_RHO (K = 5w + 15 + RHO), from try_e2.py trees."""
import pickle
ITEMS = []
for r in range(5):
    S, T, _ = pickle.load(open('tree_e2_%d.pkl' % r, 'rb'))
    ITEMS.append(('E2_%d' % r, S, T, dict(splits=0, maxstages=400), ()))
