from common import *
import mexp
from planner8 import show
exec(open('dbg2.py').read().split('for lab')[0])
S = B([tok(3)], tok(0, a=1), [BLANK]); T = B([tok(0)], tok2(8, a=1), [BLANK])
cfg = S
for i in range(12):
    ops, cfg, how = mexp.run_stuck(cfg, T)
    print(i, how, sum(o[1] for o in ops if o[0]=='steps'), show(cfg))
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 2)
    print('  loop', lp and (lp.v_at, lp.use_arg(), show(lp.X)))
    if lp is None: break
    cfg = lp.after()
print(show(T))
