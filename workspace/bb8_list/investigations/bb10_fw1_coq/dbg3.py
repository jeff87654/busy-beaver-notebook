import sys
from parts import *
s, t, pos = PARTS['S2free']
cfg = s
for k in range(30):
    ops, cfg2, how = mexp.run_stuck(cfg, t)
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        break
    cfg = lp.after()
cfg = engine.subst(cfg2, 'y', (('yp', 1),), 4)
ops, cfg2, how = mexp.run_stuck(cfg, None)
while how == 'stuck':
    lp = mexp.find_loop(cfg2, 2)
    if lp is None: break
    ops, cfg2, how = mexp.run_stuck(lp.after(), None)
W = cfg2
print('W  =', pl.show(W))
cfg = engine.subst(engine.subst(W, 'yp', (('yq', 1),), int(sys.argv[1])), 'R', (('Rq', 1),), int(sys.argv[2]))
print('W+ =', pl.show(cfg))
for k in range(40):
    ops, cfg2, how = mexp.run_stuck(cfg, None)
    print('ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), how)
    print('  at', pl.show(cfg2))
    if how != 'stuck': break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('  NO LOOP'); break
    print('  loop on', lp.v_at)
    cfg = lp.after()
