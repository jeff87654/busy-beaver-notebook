from fam import next_X
import itertools
def tonum(beta,W): return beta+1, tuple(w+1 for w in W)
def fromnum(a,cs): return a-1, tuple(c-1 for c in cs)
def pred(beta,W):
    W=list(W)
    if W and W[0]>=1:
        return beta+4, tuple([W[0]-1]+W[1:])
    j=0
    while j<len(W) and W[j]==0: j+=1
    # j = number of leading zeros
    if j==len(W):
        return 0, tuple(W+[beta+4])
    # first nonzero at index j (0-based) ; j>=1
    W2=W[:]
    W2[j]-=1
    W2[j-1]=beta+4
    return 0, tuple(W2)
bad=0;tot=0
for beta in (0,4,8,12):
    for n in range(0,5):
        for W in itertools.product((0,1,2,3),repeat=n):
            a,cs=tonum(beta,W)
            r=next_X(a,cs,N=3*10**6)
            tot+=1
            if r[0]!='X': print('NOX',beta,W,r);bad+=1;continue
            got=fromnum(*r[1])
            if got!=pred(beta,W): print('MISMATCH',beta,W,got,pred(beta,W));bad+=1
print(tot,bad)
