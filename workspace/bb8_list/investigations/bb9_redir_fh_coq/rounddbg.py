import sys
from common import *
import mexp
SUB = engine.subst
def dbg(X, vg, ivs, depth=2, maxparts=60, width=500):
    Xp = SUB(X, vg, (('v2', 1),), 1)
    Xt = SUB(X, vg, (('v2', 1),), 0)
    for iv in ivs:
        Xt = SUB(Xt, iv, ((iv, 1),), 1)
    cfg = Xp
    for k in range(maxparts):
        try:
            ops, cfg, how = mexp.run_stuck(cfg, Xt)
        except Exception as e:
            print('part', k, 'EXC', e); return
        print('part %d: %s %d steps | %s' % (k, how, sum(o[1] for o in ops if o[0] == 'steps'), pl.show(cfg)[:width]))
        if how != 'stuck': return
        lp = mexp.find_loop(cfg, depth - 1)
        print('   inner loop:', lp and (lp.v_at, lp.use_arg()))
        if lp is None:
            return
        cfg = lp.after()
