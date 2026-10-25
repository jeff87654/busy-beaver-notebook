"""python drv.py NAME [lit] : explore event NAME (from evs.EV); 'lit' first validates the spec literally."""
import sys, time, random
from evs import *
import mexp
from planner8 import show
name = sys.argv[1]
S, T = EV[name][:2]
POS = frozenset(EV[name][2]) if len(EV[name]) > 2 else frozenset()
if 'lit' in sys.argv:
    vs = sorted(engine.vars_of(S) | engine.vars_of(T))
    rnd = random.Random(1)
    for _ in range(4):
        vals = {v: rnd.randint(0, 5) for v in vs}
        r = validate.reaches(S, T, vals, max_steps=3_000_000)
        print('literal', vals, '->', r)
if 'trace' in sys.argv:
    cfg = S
    for i in range(40):
        ops, cfg, how = mexp.run_stuck(cfg, T)
        print(i, how, sum(o[1] for o in ops if o[0]=='steps'), show(cfg)[:400], flush=True)
        if how != 'stuck': break
        lp = mexp.find_loop(cfg, 2)
        print('  loop', lp and (lp.v_at, lp.use_arg()), flush=True)
        if lp is None: break
        cfg = lp.after()
    sys.exit()
t0 = time.time()
try:
    tree = mexp.explore(S, T, splits=4, positive=POS)
    print(name, 'OK %.1fs' % (time.time()-t0)); print('\n'.join(mexp.describe(tree))[:3000])
except Exception as e:
    print(name, 'FAIL %.1fs' % (time.time()-t0), e)
