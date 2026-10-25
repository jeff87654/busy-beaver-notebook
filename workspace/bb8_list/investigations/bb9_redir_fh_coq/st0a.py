import sys, pickle
from common import *
from phases import drive
import mexp
START = KF(tok(1), tok(0, 'r'), [run(Z, J=1), BLANK])
if __name__ == '__main__':
    cfg = START
    for k in range(30):
        ops, cfg, how = mexp.run_stuck(cfg)
        print('ops', sum(o[1] for o in ops if o[0]=='steps'), how, '|', pl.show(cfg)[:300])
        if how != 'stuck': break
        lp = mexp.find_loop(cfg, 2)
        if lp is None: print('NO LOOP'); break
        print('  loop on', lp.v_at)
        cfg = lp.after()
    pickle.dump(cfg, open('st0a_stuck.pkl','wb'))
