import pickle, sys, time
from common import *
from phases import drive
import mexp
S2 = KF(tok(1), tok(0, 'r'), [run(Z, m=1)] + tok(0) + tok(8) + tok(9) + tok(9) + [V('l')])
if __name__ == '__main__':
    t0 = time.time()
    cfg, how = drive(S2)
    print(how, '%.1fs' % (time.time() - t0)); print(pl.show(cfg)[:900])
    pickle.dump(cfg, open('st2_stuck.pkl', 'wb'))
