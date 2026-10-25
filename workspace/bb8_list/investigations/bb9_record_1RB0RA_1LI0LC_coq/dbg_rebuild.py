import sys
from common import *
from shapes import *
import mexp
from planner8 import show
def KK(tcount, acc, atok, mid):
    return ('B', [1, 0, 0, 1] + list(TB) * tcount + [1, 1] + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')
s = KK(0, accr(5, 'r'), tok(1), list(Z) * 11)
t = KK(6, accr(2), tok(1), list(Z) + [run(Z, r=4)] + tok(20) + tok(4) + tok(21) + tok(4))
cfg = s
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
for k in range(N):
    ops, cfg, how = mexp.run_stuck(cfg, t)
    print(k, how, ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops)[:100], '|', show(cfg)[:300], flush=True)
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 2, verbose=True)
    if lp is None:
        print('   NO LOOP; candidates', engine.candidates(cfg)); break
    print('   LOOP on', lp.v_at, 'use', lp.use_arg(), 'nested' if any(sg[0] == 'loop' for sg in lp.segs) else '')
    cfg = lp.after()
