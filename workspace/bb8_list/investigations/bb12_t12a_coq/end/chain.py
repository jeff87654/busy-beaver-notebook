"""python end/chain.py r j x A K: B-form chain from the EAT start of class r (literal events, CLR with rep 40)"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ana')
from evs_end import *
from probe import word_of, MK
from macro2 import Run, run_lit
from view import view
r, j, x, A, K = map(int, sys.argv[1:6])
S = EVE['EAT%d' % r][0]
w = word_of(S, dict(j=j, x=x, A=A - 4, K=K))
R = Run({}, verbose=False)
res = run_lit(w, len(w), 'H')
def sh(wd):
    i = wd.find(MK)
    return view(wd[i + len(MK):].lstrip('0')) if i >= 0 else '??' + view(wd)
while res[0] == 'B':
    word = res[1]
    while True:
        w2 = R.clr(word)
        if w2 is None: break
        print("   CLR from", sh(word)[-150:]); word = w2
    print(res[2], sh(word)[-150:])
    res = run_lit(word, len(word), 'H')
print(res[:3])
