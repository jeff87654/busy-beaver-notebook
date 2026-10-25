import sys, os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine
pl.set_tm(TM)
nm=sys.argv[1]
s,t=rules()[nm]
print(pl.show(s))
ops,cfg,how=engine.run_until_stuck(s,None,target=t)
print(ops,how); print(pl.show(cfg))
print('candidates',engine.candidates(cfg))
for v in engine.candidates(cfg):
    P_=engine.try_loop(cfg,v,1)
    print(v, None if P_ is None else {k:(pl.show(x) if k in('start','peeled','after') else x) for k,x in P_.items() if k in ('start','peeled','after','inserts')})
