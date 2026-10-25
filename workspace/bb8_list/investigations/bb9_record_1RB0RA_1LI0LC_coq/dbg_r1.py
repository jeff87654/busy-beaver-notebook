import sys, time
from common import *
import mexp
from planner8 import show
def left(acc, atok):
    return [1, 0, 0, 1, run(TB, t=1), 1, 1] + acc + [1] + atok + [V('l')]
start = ('B', left([run((0, 1), r=1)], [0, 1] * 3 + [run((0, 1), m=1)]), [BLANK], '>')
target = ('B', left([0, 1] * 4 + [run((0, 1), r=2)], [run((0, 1), m=1)]), [BLANK], '>')
cfg = start
for k in range(8):
    ops, cfg, how = mexp.run_stuck(cfg, target)
    print(k, how, ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), '|', show(cfg))
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 2, verbose=True)
    if lp is None: print('no loop'); break
    print('\n'.join(mexp.describe_loop(lp, '   ')))
    cfg = lp.result(((lp.v_at, 1),))
    print('   after:', show(cfg))
