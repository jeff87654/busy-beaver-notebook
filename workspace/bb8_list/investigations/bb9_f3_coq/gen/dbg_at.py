import sys
from common import *
import d0spec, mexp
exec(open('try_sub.py').read().split("print(pl.show(S))")[0].replace("int(sys.argv[1])", "4").replace("int(sys.argv[2])", "0").replace("int(sys.argv[3]) if len(sys.argv) > 3 else 6", "6"))
cfg = S
for k in range(30):
    ops, cfg2, how = mexp.run_stuck(cfg, Tg)
    if how != 'stuck': print(how); break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('STUCK at stage', k); mexp.debug_loop(cfg2, 2, 600); break
    cfg = lp.after()
