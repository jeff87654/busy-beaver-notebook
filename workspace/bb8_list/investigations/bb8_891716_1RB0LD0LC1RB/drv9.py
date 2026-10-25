import sys, os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine, validate
pl.set_tm(TM)
nm=sys.argv[1]
vals=eval(sys.argv[2])
s,t=rules()[nm]
cfg=s
for i in range(10):
    ops,c2,how=engine.run_until_stuck(cfg,None,target=t)
    print('stage',i,how,'reach(start->stuck):',validate.reaches(s,c2,vals))
    if how!='stuck': break
    lp=engine.accelerate(c2,1)
    if lp is None: break
    print('   loop',lp['v'],'result reach:',validate.reaches(s,lp['result'],vals), ' resultB reach:',validate.reaches(s,lp['resultB'],{**vals}) if False else '')
    cfg=lp['result']
print('--- loop test')
ops,c2,how=engine.run_until_stuck(s,None,target=t)
lp=engine.accelerate(c2,1)
for cval in (1,2,3,4):
    v={**vals,'c':cval}
    print('c=',cval,'stuck->result:',validate.reaches(c2,lp['result'],v))
print(pl.show(c2)); print(pl.show(lp['result']))
print(validate.concretize(lp['result'],{**vals,'c':2}))
print('--- round test', lp['v2'], lp['inserts'])
print(pl.show(lp['peeled'])); print(pl.show(lp['after']))
for c0 in (0,1,2,3):
    print(c0, validate.reaches(lp['peeled'],lp['after'],{**vals,lp['v2']:c0}))
