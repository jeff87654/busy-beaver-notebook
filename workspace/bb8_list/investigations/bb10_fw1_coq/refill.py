import sys
from parts import *
c = int(sys.argv[1]); peels = [(a.split(':')[0], int(a.split(':')[1])) for a in sys.argv[2:]]
S = W2(dict(w=1), None, dict(k=1), pre_w=int(__import__("os").environ.get("PREW", "1")), beyond=[1, V('l')], extra_zeros=c, zblk=5)
cfg = S
while True:
    ops, cfg2, how = mexp.run_stuck(cfg, None)
    if how != 'stuck':
        print(how, pl.show(cfg2)); break
    lp = mexp.find_loop(cfg2, 2)
    if lp is not None:
        cfg = lp.after(); continue
    if not peels:
        print('NO LOOP at', pl.show(cfg2)); break
    v, k = peels.pop(0)
    cfg = engine.subst(cfg2, v, ((v, 1),), k)
