from common import *
import mexp, sys
s = G(grp(0, B=1) + [run(Z, k=1)] + list(Z) * 2 + grp(3, n=1) + [1, V('l')])
t = G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, B=1) + grp(1, n=1) + [1, V('l')])
cfg = s
for st in range(3):
    ops, cfg, how = mexp.run_stuck(cfg, t)
    lp = mexp.find_loop(cfg, 2)
    cfg = lp.after()
print('stage3 start', pl.show(cfg))
print('target      ', pl.show(t))
print('target canon', pl.canon(t))
# step through stage 3 manually with crossings
for i in range(80):
    try:
        pl.head(cfg)
        cfg = pl.step(cfg)
    except pl.Stuck:
        r, why = pl.try_crossing(cfg)
        if r: cfg = r[0]; print('  cross')
        else:
            a = pl.try_align(cfg)
            if a: cfg = a[0]; print('  align')
            else: print('stuck', why); break
    if cfg[0] == 'G': print(i, pl.show(cfg)); print('   canon', pl.canon(cfg))
