import sys, time
from common import *
from d0spec import *
import mexp
exec(open('try_sub3.py').read().split('print(pl.show(S))')[0])
cfg = S
for k in range(30):
    ops, cfg2, how = mexp.run_stuck(cfg, Tg)
    print('stage', k, how, sum(o[1] for o in ops if o[0] == 'steps'), pl.show(cfg2)[:400])
    if how != 'stuck': break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        mexp.debug_loop(cfg2, 2, 500); break
    print('  loop on', lp.v_at); cfg = lp.after()
