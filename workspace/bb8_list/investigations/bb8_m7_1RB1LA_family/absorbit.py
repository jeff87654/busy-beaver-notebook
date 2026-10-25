# abstract model on W (nearest first) and b; count macro events, report R4 epochs. Uses the proved family rules.
import sys
def step(W,b):
    # returns (W',b',kind)
    j=0
    while j<len(W) and W[j]==0: j+=1
    if j==len(W):
        return [2]*(b+1),0,'R4'
    if j==0:
        W=list(W); W[0]-=1; return W,b+1,'R1'
    y1=W[j]; t=W[j+1:]
    if j<=b:  # R3A with k=j-1, r=b-j
        k=j-1; r=b-j
        return [2]*k+[2*r+4,y1-1]+t,0,'R3A'
    if j==b+1:
        return [2]*b+[y1+2]+t,0,'R3B'
    m=j-b-2
    return [2]*(b+1)+[0]*m+[y1]+t,0,'R3C'
W=[2,2];b=0;n=0
epochs=[]
from collections import Counter
cnt=Counter()
while n<int(sys.argv[1]) and len(epochs)<3:
    # fast-forward R1: a steps
    if W[0]>0:
        a=W[0]; W=[0]+W[1:]; b+=a; n+=a; cnt['R1']+=a; continue
    W,b,k=step(W,b); n+=1; cnt[k]+=1
    if k=='R4':
        epochs.append((n,len(W)-1,'listlen',len(W),'b=0'))
        print('R4 at event',n,'new list length',len(W),'b before rebuild was',len(W)-1)
print(cnt)
