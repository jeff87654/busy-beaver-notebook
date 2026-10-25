from common import *
import mexp
from planner8 import show
def H(left): return ('H', list(left), [BLANK], '>')
def B(ts, acc, far):
    left = list(acc) + tok(0)
    for t in reversed(ts): left += t
    return H(left + far)
S = B([tok(3, t=1)], tok(0, a=1), [V('l')])
T = B([tok(0, t=1)], tok(8, a=2), [V('l')])
cfg = S
for i in range(6):
    ops, cfg, how = mexp.run_stuck(cfg, T)
    print(i, how, sum(o[1] for o in ops if o[0]=='steps'), show(cfg))
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 2)
    print('  loop', lp and (lp.v_at, show(lp.X)))
    if lp is None: break
    cfg = lp.after()
print('---- t=0 with blank left')
S0 = B([tok(3)], tok(0, a=1), [BLANK])
T0 = B([tok(0)], tok(8, a=2), [BLANK])
tree = mexp.explore(S0, T0, splits=2)
print('\n'.join(mexp.describe(tree))[:3000])
