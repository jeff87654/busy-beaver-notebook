import sys
from common import *
from shapes import *
import mexp
from planner8 import show
def KK(tcount, acc, atok, mid):
    return ('B', [1, 0, 0, 1] + list(TB) * tcount + [1, 1] + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')
s = KK(6, accr(5, 'r'), tok(1), list(Z) * 11 + [run(Z * 5, q=1)] + tok(2) + tok(4) + tok(21) + tok(4))
t = KK(8, accr(4), tok(0), list(Z) * 4 + [run(Z * 3, q=1)] + tok(11, 'q', (0, 1) * 3) + tok(8, 'r', (0, 1, 0, 1)) + tok(2) + tok(21) + tok(4))
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

def concrete_word(cfg, vals):
    """tape word (left to right) and head index, state"""
    q, L, s, R = validate.concretize(cfg, vals)
    left = ''.join(map(str, reversed(L)))
    return left + str(s) + ''.join(map(str, R)), len(left), q
