import sys, pickle
from macro2 import *
k, w, f = map(int, sys.argv[1:4]); out = sys.argv[4]
R = Run({}, verbose=True)
wd = r1end(k, w, f)
r = R.go(wd, len(wd), 'H')
pickle.dump(R.events, open(out, 'wb'))
