import sys
from tr import *
word=sys.argv[1]; maxs=int(sys.argv[2]); K=int(sys.argv[3])
cnt=[0]
# find steps where machine in state E reading 0
t=parse(M); SZ=1<<22; tp=[0]*SZ; off=SZ//2
for i,ch in enumerate(word): tp[off+i]=int(ch)
p=off+len(word); q=1; lo=off; hi=off+len(word)-1
for st in range(maxs):
    c=tp[p]
    if q==4 and c==0:
        cnt[0]+=1
        print("E0 read at step",st,"head",p-off,"tape:",rle(tp,lo,hi))
        if cnt[0]>=K: break
    tr=t[(q,c)]
    if tr is None: print("HALT",st); break
    tp[p]=tr[0]; p+=tr[1]; q=tr[2]; lo=min(lo,p); hi=max(hi,p)
