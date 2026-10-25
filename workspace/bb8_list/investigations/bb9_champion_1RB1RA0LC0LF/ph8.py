import sys
import planner9 as pl
from planner9 import *
s0=int(sys.argv[1]); I=int(sys.argv[2]); N=int(sys.argv[3]) if len(sys.argv)>3 else 100
Lc=[1]*s0+[0,1,1]*I+[BLANK]
cfg=('A',norm_side(Lc),[BLANK],'>')
n=0
print(n,show(cfg))
while n<N:
    try: cfg=step(cfg)
    except Exception as e:
        print('stop',e); break
    n+=1
    print(n,show(cfg))
