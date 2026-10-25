import time, pickle, sys
from common import *
from phases import drive_peel
from st3y import Y
def Y0z(c, per=5):
    y = engine.subst(Y(), 'T', (), 0)
    q, L, R, mode = y
    R2 = []
    for t in R:
        if t == ('run', Z, (('z', 1),)):
            R2 += list(Z) * c + [run(Z * per, u=1)]
        else:
            R2.append(t)
    return (q, L, R2, mode)
if __name__ == '__main__':
    for c in map(int, sys.argv[1:]):
        t0 = time.time()
        cfg, how, peels = drive_peel(Y0z(c), {'a', 'u'}, verbose=False)
        print('c=%d' % c, how, peels, '%.1fs' % (time.time() - t0), pl.show(cfg)[:700], flush=True)
        pickle.dump((cfg, peels), open('st3x_c%d.pkl' % c, 'wb'))
