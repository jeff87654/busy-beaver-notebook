import sys
import planner9 as pl
from planner9 import *
# concrete: L = 1^s (0 1 1)^K 0 1 1 0 BLANK ; R = 0 1 1^y t(=0 BLANK)
s=int(sys.argv[1]); K=int(sys.argv[2]); y=int(sys.argv[3])
Lc=[1]*s+[0,1,1]*K+[0,1,1,0,BLANK]
Rc=[0,1]+[1]*y+([0]+[1]*int(sys.argv[4])+[0,BLANK] if len(sys.argv)>4 else [0,BLANK])
cfg=('A',norm_side(Lc),norm_side(Rc),'>')
n=0
print(n,show(cfg))
while n<400:
    try:
        cfg=step(cfg)
    except Exception as e:
        print('stop',e); break
    n+=1
    print(n,show(cfg))
