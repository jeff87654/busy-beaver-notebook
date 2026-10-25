from t6 import *
import inst
cfg=seen[-1]
for s in range(0,5):
    p=inst.k_of(cfg,{'s':s})
    print('s=',s,None if p is None else (len(p[0]),p[0][:2],p[1],p[2]))
