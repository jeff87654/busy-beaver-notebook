import sys, time
from common import *
import mexp
def H(left):
    return ('H', list(left), [BLANK], '>')
def B(ts, acc, far):
    """B-form: ts = token items left-to-right (each a list stream for one token), acc = token stream"""
    left = list(acc) + tok(0)
    for t in reversed(ts):
        left += t
    return H(left + far)
t0 = time.time()
S = B([tok(3, t=1)], tok(0, a=1), [V('l')])
T = B([tok(0, t=1)], tok(8, a=2), [V('l')])
tree = mexp.explore(S, T, splits=2)
print('\n'.join(mexp.describe(tree))[:5000])
print('R1 %.1fs' % (time.time()-t0))
t0 = time.time()
S = B([tok(3, t=1), tok(1), run([1,0,1], k=1)], tok(0, a=1), [V('l')])
T = B([tok(0, t=1), tok(3, a=1), run([1,0,1], k=1)], tok(4), [V('l')])
tree = mexp.explore(S, T, splits=2)
print('\n'.join(mexp.describe(tree))[:5000])
print('R2 %.1fs' % (time.time()-t0))
