import sys
from rules884 import *
import engine, validate
pl.set_tm(TM)
rl = dict((n,(s,t)) for n,s,t in rules())
start3, _ = rl['R3m']
TT = [1, 1, V('t')]
def M3(extra=0):
    return ('E', [('run', (1,0,1,0), (('b',1),)), BLANK],
            [('run',(1,1),(('k',1),))] + [1]*5 + [0,1]*4 + [1,1] + mkrun(U, {'y':1}) + TT, '<')
def G3():
    return ('A', [BLANK], pl.norm_side(mkrun((1,1),{'k':1},0) + [1]*6 + mkrun(U2, {'b':1}) + [0,1]*3 + [1,1] + mkrun(U, {'y':1}) + TT), '<')
# note: '<' with L=[BLANK]: head cell is the blank to the left of R
for vals in ({'k':0,'b':1,'y':2},{'k':1,'b':2,'y':1},{'k':2,'b':2,'y':2}):
    # t is a VAR side: represented by marker in concretize
    print(vals, 'M3 reached after', validate.reaches(start3, M3(), vals), ' G3 after', validate.reaches(start3, G3(), vals))
