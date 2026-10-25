import sys
from rules884 import *
import engine, validate
pl.set_tm(TM)
rl = dict((n,(s,t)) for n,s,t in rules())
start3, tgt3 = rl['R3m']
s0 = engine.subst(start3, 'k', (), 0)
ops, C, how = engine.run_until_stuck(s0, None)
print(how, pl.show(C))
for st in range(2):
    pass
vals = {'b':1,'y':2}
print('reach', validate.reaches(s0, C, vals))
q,l,h,r = validate.concretize(C, vals)
print(q, ''.join(map(str,l[::-1])), h, ''.join(map(str,r)))
