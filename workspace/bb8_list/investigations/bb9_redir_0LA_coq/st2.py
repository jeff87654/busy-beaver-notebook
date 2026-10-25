import sys, pickle
from common import *
from phases import *
import mexp
START = KR(tok(1), tok(1, 'r'), [run(Z, m=1)] + tok(0) + tok(8) + [V('l')])
cfg, how = drive(START, verbose=False)
cfg = regroup(cfg, 'm', 5, 0, 'u')
cfg, how = drive(cfg, verbose=False)
pickle.dump(cfg, open('st2_p2end.pkl', 'wb'))
print(pl.show(cfg))
