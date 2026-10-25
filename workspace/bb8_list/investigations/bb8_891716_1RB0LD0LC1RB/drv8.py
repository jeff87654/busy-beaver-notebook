import sys, os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
from rules891 import *
import engine, validate
pl.set_tm(TM)
s,t=rules()['R3Bm']
cfg=s
for i in range(10):
    ops,cfg,how=engine.run_until_stuck(cfg,None,target=t)
    if how!='stuck': break
    lp=engine.accelerate(cfg,1)
    if lp is None: break
    cfg=lp['result']
print(pl.show(cfg))
vals={'c':3,'y':1}
cc=validate.concretize(cfg,vals)
print(cc)
print(validate.reaches(s,cfg,vals))
print('start->target', validate.reaches(s,t,vals))
sa,ta=rules()['R1m']
print('R1', validate.reaches(sa,ta,{'a':2,'b':3}))
