import sys, itertools, random
from cyc import *
from enum1 import cycle
def one(n,R,maxsteps=3*10**6):
    kind,k,res,reach=cycle(n,R,maxsteps)
    return kind,k,res,reach
def analyze(p,n,tails):
    outs=[]
    for t in tails:
        R=p+t
        kind,k,res,reach=one(n,R)
        if kind!='stop': return (kind,k,reach)
        Lr,Rr,pos=res
        outs.append((Lr,Rr,R,reach))
    return outs
if __name__=='__main__':
    n=int(sys.argv[1]); Lp=int(sys.argv[2])
    random.seed(1)
    tails=[''.join(random.choice('01') for _ in range(30))+'0'*30 for _ in range(3)]
    for combo in itertools.product('01',repeat=Lp):
        p=''.join(combo)
        outs=analyze(p,n,tails)
        if isinstance(outs,tuple): print(p,outs); continue
        # common-suffix-based prefix rewriting
        rs=[]
        for Lr,Rr,R,reach in outs:
            # find longest common suffix of R and Rr
            i=0
            while i<min(len(R),len(Rr)) and R[-1-i]==Rr[-1-i]: i+=1
            rs.append((R[:len(R)-i],Rr[:len(Rr)-i],i,Lr))
        print(p,'|',[ (a,b) for a,b,i,L in rs][:3],'Llen',[len(L) for a,b,i,L in rs])
