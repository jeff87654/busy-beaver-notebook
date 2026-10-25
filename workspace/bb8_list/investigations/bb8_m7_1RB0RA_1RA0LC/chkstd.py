from batch import *
import random, sys
random.seed(int(sys.argv[1])); n=int(sys.argv[2])
cfgs=[]
def pred(toks,r):
    a=toks[-1]
    if a>=4: return toks[:-1]+[a-3],2*r+4
    j=len(toks)-2
    while j>=0 and toks[j]==1: j-=1
    if j<0: return None
    new=list(toks); new[j]-=3; new[j+1]=2*r+3
    return new,2
for _ in range(n):
    L=random.randint(1,8)
    toks=[random.choice([1,1,1,4,7,10,13,16,19,22]) for _ in range(L)]+[random.choice([1,1,4,7,10])]
    r=random.choice([2,5,8,11,14,20])
    if pred(toks,r) is None: continue
    cfgs.append((toks,r))
res=run(cfgs,tail='111001',N=500000000)
bad=0;to=0
for t,r,x in res:
    if not isinstance(x,tuple): to+=1; print('NOK',t,r,x); continue
    p=pred(t,r)
    if (x[1],x[2])!=p: bad+=1; print('MISMATCH',t,r,x[1],x[2],'pred',p)
print('standard-list check',len(cfgs),'bad',bad,'notK',to)
