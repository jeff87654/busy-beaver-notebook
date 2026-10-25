import pickle, sys
from st0 import *
W0 = pickle.load(open('W0.pkl', 'rb'))
W1 = merge_zeros(W0)
# peel one zero and run; print the stuck points of one pass in detail
P = engine.subst(W1, 'Z', (('Zp', 1),), 1)
cfg = P
for i in range(12):
    ops, C, how = mexp.run_stuck(cfg, None)
    print(i, how, ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops)[:150])
    print('   ', pl.show(C)[-330:])
    if how != 'stuck': break
    lp = mexp.find_loop(C, 1)
    if lp is None:
        print('NO LOOP'); break
    print('    loop on', lp.v_at, 'X =', pl.show(lp.X)[-200:])
    cfg = lp.after()
