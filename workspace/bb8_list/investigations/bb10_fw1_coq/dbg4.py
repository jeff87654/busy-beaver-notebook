"""python dbg4.py PART peel1 peel2 ...   peel = var:k (substitute var -> var+k at the next NO LOOP)"""
import sys
from parts import *
s, t, pos = PARTS[sys.argv[1]]
peels = [p.split(':') for p in sys.argv[2:]]
cfg = s
while True:
    ops, cfg2, how = mexp.run_stuck(cfg, t)
    print('ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), how)
    print('  at', pl.show(cfg2))
    if how != 'stuck':
        break
    lp = mexp.find_loop(cfg2, 2)
    if lp is not None:
        print('  loop on', lp.v_at)
        cfg = lp.after(); continue
    if not peels:
        print('  NO LOOP'); break
    v, k = peels.pop(0)
    print('  PEEL', v, k)
    cfg = engine.subst(cfg2, v, ((v, 1),), int(k))
