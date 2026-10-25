import pickle, sys
from st0 import *
import os
if os.path.exists('W0.pkl'):
    W0 = pickle.load(open('W0.pkl', 'rb'))
else:
    W0 = find_w0(); pickle.dump(W0, open('W0.pkl', 'wb'))
W1 = merge_zeros(W0)
cont(W1, [(a.split(':')[0], int(a.split(':')[1])) for a in sys.argv[1:]])
