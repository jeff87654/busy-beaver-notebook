import sys, time
sys.path.insert(0, '.')
from evs_end import *
import mexp
from planner8 import show
S, T = EVE[sys.argv[1]][:2]
cfg = S
for it in range(10):
    ops, cfg, how = mexp.run_stuck(cfg, T)
    s = show(cfg)
    print(it, how, sum(o[1] for o in ops if o[0] == 'steps'), s[:2000] if 'j' in s.split('>')[0][-300:] or '{j}' in s else '')
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 1)
    if lp is None: print('no loop'); break
    print('  loop on', lp.v_at, 'ivs', lp.ivs, 'X =', show(lp.X)[:3000] if lp.v_at == 'j' or lp.v_at.startswith('j') else '')
    cfg = lp.after()
    if lp.v_at.startswith('j'):
        print('AFTER', show(cfg)); break
