import random
from f24n import nstep
random.seed(5)
def rule(L):
    L=list(L); y=L[-1]
    if len(L)>=2 and L[-2]>=1: return tuple(L[:-2]+[L[-2]-1,y+2])
    z=0
    while z<len(L)-1 and L[-2-z]==0: z+=1
    if z==len(L)-1: # all zero left of y
        return {1:(y+1,),2:(y,3),3:(y-1,2,3),4:(y-2,4,2,3)}.get(z)
    a=L[-2-z]; pre=L[:-2-z]+[a-1]
    if z==1: return tuple(pre+[y+1,3])
    if z==2: return tuple(pre+[y,2,3])
    if z==3: return tuple(pre+[y-1,4,2,3])
    if z==4: return 'H'
cases=[]
for i in range(500):
    n=random.randint(2,7); L=[random.choice([0,0,1,1,2,3,5,9]) for _ in range(n-1)]+[random.randint(3,30)]
    if L[-2]>=1 and random.random()<0.6: L[-2]=0
    if 0 not in L[:-1] or random.random()<0.5:
        k=random.randint(1,min(4,n-1)); L[-1-k:-1]=[0]*k
    z=0
    while z<len(L)-1 and L[-2-z]==0: z+=1
    if z==len(L)-1 and z>4: continue
    if z>4: continue
    cases.append(tuple(L))
out=nstep(cases)
bad=0; from collections import Counter; kinds=Counter()
for L,(o,ne) in zip(cases,out):
    e=rule(L); g='H' if o and o[0]=='H' else o
    z=0
    while z<len(L)-1 and L[-2-z]==0: z+=1
    kinds[(z, z==len(L)-1)]+=1
    if g!=e:
        bad+=1
        if bad<6: print('BAD',L,g,e)
print(len(cases),'cases',bad,'bad',dict(kinds))
