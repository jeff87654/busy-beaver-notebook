import sys
from parts import *
name = sys.argv[1]
s, t, pos = PARTS[name]
cfg = s
nstages = int(sys.argv[2])
for k in range(nstages):
    ops, cfg2, how = mexp.run_stuck(cfg, t)
    if how != 'stuck':
        print(how); break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('  NO LOOP at', pl.show(cfg2)); break
    cfg = lp.after()
# now peel variable
v = sys.argv[3]
cfg = engine.subst(cfg2, v, ((v + 'p', 1),), int(sys.argv[4]) if len(sys.argv) > 4 else 1)
print('peeled:', pl.show(cfg))
for k in range(12):
    ops, cfg2, how = mexp.run_stuck(cfg, None)
    print('ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), how)
    print('  at', pl.show(cfg2))
    if how != 'stuck': break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('  NO LOOP'); break
    print('  loop on', lp.v_at)
    cfg = lp.after()
