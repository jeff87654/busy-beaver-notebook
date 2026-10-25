"""Group 'e1': key-31 entry E1_E (E = P mod 6 class), from try_e1.py trees."""
import pickle
ITEMS = []
for E in range(6):
    S, T, _ = pickle.load(open('tree_e1_%d.pkl' % E, 'rb'))
    ITEMS.append(('E1_%d' % E, S, T, dict(splits=0, maxstages=400), ()))
