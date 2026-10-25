import sys
import planner9 as pl
from planner9 import *
b=int(sys.argv[1]); k=int(sys.argv[2])
# top-first ds = 0^k, 2, 5 ; a=0
def lft(ds):
    out=[]
    for d in ds: out += [0]+[1]*d
    return out
ds=[0]*k+[2,5]
R=[1]*(b+1)+[0]+[0]*0+lft(ds)+[BLANK]
# a=0: tape [1^(b+1)] 0 [1^a] lft ds  -> 1^(b+1),0, (a=0 none), then lft ds
cfg=('D',[BLANK],norm_side(R),'<')
n=0
print(n,show(cfg))
last=None
while n<2000:
    cfg=step(cfg); n+=1
    q,L,Rr,mode=cfg
    if q=='A' and mode=='>' and Rr[0]==0 and (len(Rr)>1 and Rr[1]==1) :
        print(n,show(cfg)); 
    if q=='D' and ((mode=='<' and L==[BLANK]) or (mode=='>' and L==[BLANK] and Rr[0]==0)) and n>5: print('K?',n,show(cfg)); break
