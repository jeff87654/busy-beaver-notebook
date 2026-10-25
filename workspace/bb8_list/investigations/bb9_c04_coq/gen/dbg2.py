import sys
from common import *
import d0spec, mexp
src = open('try_sub.py').read().split("print(pl.show(S))")[0]
src = src.replace("int(sys.argv[1])", "4").replace("int(sys.argv[2])", "0").replace("int(sys.argv[3]) if len(sys.argv) > 3 else 6", "6").replace("int(sys.argv[4]) if len(sys.argv) > 4 else 6", "6")
exec(src)
cfg = S
for k in range(30):
    ops, cfg2, how = mexp.run_stuck(cfg, Tg)
    if how != 'stuck': print(how); break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('STUCK at stage', k)
        for var in mexp.absorb_variants(cfg2):
            if len(var) > 3:
                S2, v = var[:2]
                print('ROT variant', pl.show(S2)[:300])
                v2 = mexp.fresh(v); P = mexp.subst(S2, v, ((v2, 1),), 1); S1 = mexp.subst(S2, v, ((v2, 1),), 0)
                ops, C, how = mexp.run_stuck(P)
                print(' round:', how, sum(o[1] for o in ops if o[0]=='steps'), pl.show(C)[:400])
                print(' S1   :', pl.show(S1)[:400])
                print(' match', mexp.match_shift_multi(S1, C))
        break
    cfg = lp.after()
