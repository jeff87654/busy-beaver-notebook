from common import *
from shapes import *
import mexp, gen_reb1
S = gen_reb1.START; Tg = gen_reb1.TARGET
print('S', pl.show(S)[:200]); print('T', pl.show(Tg)[:200])
cfg = S
for k in range(40):
    try:
        ops, cfg2, how = mexp.run_stuck(cfg, Tg, budget=2000000)
    except Exception as e:
        print('stage', k, 'EXC', e, pl.show(cfg)[:200]); break
    print('stage', k, how, sum(o[1] for o in ops if o[0]=='steps'), pl.show(cfg2)[:160])
    if how != 'stuck': break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('  no loop'); break
    print('  loop on', lp.v_at); cfg = lp.after()
