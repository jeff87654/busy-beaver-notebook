import sys
from parts import *
name = sys.argv[1]
s, t, pos = PARTS[name]
cfg = s
for k in range(int(sys.argv[2]) if len(sys.argv) > 2 else 10):
    ops, cfg2, how = mexp.run_stuck(cfg, t)
    print('ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), how)
    print('  at', pl.show(cfg2))
    if how != 'stuck':
        break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('  NO LOOP'); break
    print('  loop on', lp.v_at, 'X =', pl.show(lp.X))
    cfg = lp.after()
    print('  after', pl.show(cfg))
