import sys, pickle, time
from common import *
from phases import drive
import mexp
START2 = KR(tok(1), tok(1, 'r'), [run(Z * 5, u=1)] + tok(0) + tok(8) + [V('l')])
t0 = time.time()
cfg, how = drive(START2)
print(how, '%.1fs' % (time.time() - t0)); print(pl.show(cfg)[:1500])
pickle.dump(cfg, open('st2e_end.pkl', 'wb'))
