from common import *
import mexp, time
from planner8 import show
def H(left): return ('H', list(left), [BLANK], '>')
def W(*toks, far=None):
    """tape of tokens left-to-right (each a stream), head H on the blank right of it"""
    left = []
    for t in reversed(toks): left += t
    return H(left + (far if far is not None else [V('l')]))
for lab, S, T in [
  ('PASS', W(tok(1, c=1), tok(0, j=1)), W(tok(0, c=1), tok(2, j=1))),
  ('PRO', W(tok(3, t=1), tok(0), tok(0, a=1)), W(tok(0, t=1), tok(3, a=1), tok(2))),
]:
    t0 = time.time()
    try:
        tree = mexp.explore(S, T, splits=3)
        print(lab, 'OK %.1fs' % (time.time()-t0)); print('\n'.join(mexp.describe(tree))[:2500])
    except Exception as e:
        print(lab, 'FAIL %.1fs' % (time.time()-t0), e)
