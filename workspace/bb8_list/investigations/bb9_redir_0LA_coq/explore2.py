import sys, time
from common import *
import mexp
NC = int(sys.argv[1]); PER = int(sys.argv[2])
START = KR(tok(1), tok(1, 'r'), list(Z) * NC + [run(Z * PER, j=1)] + tok(0) + tok(8) + [V('l')])
cfg = START
for k in range(40):
    ops, cfg, how = mexp.run_stuck(cfg)
    print('ops', sum(o[1] for o in ops if o[0]=='steps'), len(ops), how)
    print('   ', pl.show(cfg)[:600])
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 2)
    if lp is None: print('no loop'); break
    print('LOOP on', lp.v_at)
    cfg = lp.after(); print('  after', pl.show(cfg)[:600])
