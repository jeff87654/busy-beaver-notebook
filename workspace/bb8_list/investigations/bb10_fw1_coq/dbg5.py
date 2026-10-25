import sys, os
from parts import *
c = 17; zb = 10; prew = 16
S = W2(dict(w=1), None, dict(k=1), pre_w=prew, beyond=[1, V('l')], extra_zeros=c, zblk=zb)
cfg = S
while True:
    ops, cfg2, how = mexp.run_stuck(cfg, None)
    lp = mexp.find_loop(cfg2, 2)
    if lp is None: break
    cfg = lp.after()
print(pl.show(cfg2)[:200])
# manual: peel k and run until stuck, show
P = engine.subst(cfg2, 'k', (('kk', 1),), 1)
for i in range(6):
    ops, C, how = mexp.run_stuck(P, None)
    print('ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), how)
    print(' C=', pl.show(C)[:260])
    lp = mexp.find_loop(C, 1)
    if lp is None: print('noloop'); break
    print(' loop', lp.v_at); P = lp.after()
