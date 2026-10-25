import sys
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
rets=[]
for step in range(700000):
    s=tape.get(pos,0)
    if pos==-2 and q==7: rets.append(step)
    w,d,nq=T[(q,s)]
    tape[pos]=w; pos+=1 if d=='R' else -1; q=nq
# frontier extension times (known): 
ext=[4002,13238,28078,57998,118332,349732,703168,1410440,2825638,8244270]
big=[r for r in rets]
import bisect
def count(lo,hi,minint):
    c=0
    for i in range(1,len(rets)):
        if lo<=rets[i]<hi and rets[i]-rets[i-1]>minint: c+=1
    return c
for lo,hi in zip(ext,ext[1:]):
    n=sum(1 for r in rets if lo<=r<hi)
    print(lo,hi,'returns',n,'group-heads(int>150)',count(lo,hi,150),'ratio steps',hi/lo)
