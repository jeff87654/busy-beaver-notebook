import sys
import rules_r4, coqgen
from rules884 import *
import engine
pl.set_tm(TM)
name, s, t, prog = rules_r4.pieces()[0]
tree = engine.explore(s, t)
lp = [it for it in tree['items'] if it[0]=='loop'][0][1]
# replicate loop_lemma framing
S, v, v2 = lp['start'], lp['v'], lp['v2']
S1 = engine.subst(S, v, ((v2, 1),), 0)
sides=[]
for i in (1,2):
    toks = engine.side_tokens(S1[i])
    pos, ins = lp['inserts'][i-1]
    toks = [('run', t_[1], tuple((('j' if k == v2 else k), c) for k, c in t_[2])) if pl.is_run(t_) else t_ for t_ in toks]
    if ins:
        sides.append(toks[:pos] + [('VAR', 'w%d' % i)])
    else:
        sides.append(toks)
Xb = (S1[0], pl.norm_side(sides[0]), pl.norm_side(sides[1]), S1[3])
step = engine.subst(Xb, 'j', (('j',1),), 2)
print('step:', pl.show(step))
ops, C, how = engine.run_until_stuck(step, None)
print(how, pl.show(C))
