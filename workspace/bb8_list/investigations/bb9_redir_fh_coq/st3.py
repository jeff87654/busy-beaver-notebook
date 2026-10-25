import pickle, sys, time
from common import *
from phases import drive_peel
S3 = KF(tok(1), tok(0, 'r'), list(Z) + [run(Z * 5, u=1)] + tok(0) + tok(0, 't', (1, 0) * 3) + tok(8) + [V('l')])
if __name__ == '__main__':
    t0 = time.time()
    cfg, how, peels = drive_peel(S3, {'r', 't', 'u'}, verbose=False)
    print(how, peels, '%.1fs' % (time.time() - t0)); print(pl.show(cfg)[:1200])
    pickle.dump((cfg, peels), open('st3_stuck.pkl', 'wb'))
