import sys, pickle
from parts import *
S = W2(dict(w=1), None, dict(k=1), pre_w=16, beyond=[1, V('l')], extra_zeros=17, zblk=10)
cfg = S
while True:
    ops, cfg2, how = mexp.run_stuck(cfg, None)
    lp = mexp.find_loop(cfg2, 2)
    if lp is None: break
    cfg = lp.after()
pickle.dump(cfg2, open('stuckC.pkl', 'wb'))
P = engine.subst(cfg2, 'k', (('kk', 1),), 1)
for i in range(12):
    ops, C, how = mexp.run_stuck(P, None)
    print('ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), how)
    print(' C=', pl.show(C)[:330])
    lp = mexp.find_loop(C, 1)
    if lp is None: print('noloop'); break
    print(' loop', lp.v_at); P = lp.after()
