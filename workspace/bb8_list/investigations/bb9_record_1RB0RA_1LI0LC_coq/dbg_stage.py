"""Follow the explorer's stages on one configuration, printing stuck points and loop attempts."""
import sys
from common import *
from shapes import *
import mexp
from planner8 import show
def trace(s, t, n=12):
    cfg = s
    for k in range(n):
        ops, cfg, how = mexp.run_stuck(cfg, t)
        print(k, how, ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops)[:120], '|', show(cfg)[:250])
        if how != 'stuck': return
        lp = mexp.find_loop(cfg, 2, verbose=True)
        if lp is None:
            print('   NO LOOP; candidates', engine.candidates(cfg)); return
        print('\n'.join(mexp.describe_loop(lp, '   '))[:1500])
        cfg = lp.after()
rest = [1, 0, V('l')]
def K2(acc, atok, mid):
    return ('B', tailpart() + acc + atok + mid + rest, [BLANK], '>')
s = K2(accr(1, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'x'))
t = K2(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x'))
t = engine.subst(t, 'r', (('r', 1),), 1)
trace(s, t)
