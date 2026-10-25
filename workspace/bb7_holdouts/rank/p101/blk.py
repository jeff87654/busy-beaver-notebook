"""blk.py: block representation. tape (mirrored, left->right) = blocks of 1s at spacing 2, separated by gaps G>=2 (number of 0s).
Repr list [n1,G1,n2,G2,...,nk]. follow_blocks(M, word, steps, maxev) -> list of (step, repr) at events (B on blank right of all)."""
import idle, sys
from sim import parse
def blocks(s):
    s=s.strip('0'); ones=[i for i,ch in enumerate(s) if ch=='1']
    r=[1]
    for x,y in zip(ones,ones[1:]):
        g=y-x-1
        if g==1: r[-1]+=1
        else: r+= [g,1]
    return r
def word_of(r):
    w=''
    for i,x in enumerate(r):
        if i%2==0: w+='0'.join('1'*x)
        else: w+='0'*x
    return w
def kword(ds,a,b,P='101'):
    w=P
    for d in ds: w+='10'*d+'00'
    return w+'10'*a+'00'+'10'*(2*b+1)+'1'
def comp(r):
    # run-length compress repeated (n,G) pairs
    o=[];i=0
    while i<len(r):
        if i%2==0 and i+3<len(r):
            j=i; 
            while j+3<len(r) and r[j]==r[i] and r[j+1]==r[i+1]: j+=2
            k=(j-i)//2
            if k>=2: o.append('(%d/%d)^%d'%(r[i],r[i+1],k)); i=j; continue
        o.append(str(r[i]) if i%2==0 else '/%d/'%r[i]); i+=1
    return ' '.join(o)
def follow_blocks(M,w,steps,maxev,Q=1,tapesize=1<<22):
    tr=parse(M)
    T=bytearray(tapesize); off=tapesize//2
    for i,ch in enumerate(w): T[off+i]=ch=='1'
    p=off+len(w); q=Q; lo=off; hi=off+len(w)-1; ev=0; out=[]
    for st in range(steps):
        c=T[p]; t=tr[(q,c)]
        if t is None: out.append(('H',st,sum(T))); return out
        T[p]=t[0]
        if t[0]: lo=min(lo,p); hi=max(hi,p)
        p+=t[1]; q=t[2]
        if q==Q and T[p]==0 and p>hi:
            while hi>lo and not T[hi]: hi-=1
            if p>hi:
                while lo<hi and not T[lo]: lo+=1
                s=bytes(T[lo:hi+1]).replace(b'\x00',b'0').replace(b'\x01',b'1').decode()
                out.append((st+1,p-hi-1,blocks(s)))
                ev+=1
                if ev>=maxev: return out
    out.append(('T',steps)); return out
def isR1(prev,r):
    # last block +2, previous block -1 (a-block), same else
    if len(prev)!=len(r): 
        # a-block vanished: prev [...,G,1,3,nk] -> [..., G+2+?...]
        return False
    return prev[:-3]==r[:-3] and r[-1]==prev[-1]+2 and r[-3]==prev[-3]-1 and r[-2]==prev[-2]
if __name__=='__main__':
    M=sys.argv[1]; w=sys.argv[2]
    if w.startswith('K:'):
        _,ds,a,b=w.split(':'); w=kword([int(x) for x in ds.split(',')] if ds else [],int(a),int(b))
    elif w.startswith('B:'):
        w=word_of([int(x) for x in w[2:].split(',')])
    out=follow_blocks(M,w,int(sys.argv[3]),int(sys.argv[4]))
    full=len(sys.argv)>5
    prev=None
    for e in out:
        if e[0] in ('H','T'): print(e); break
        st,gap,r=e
        if full or not (prev and isR1(prev,r)): print(st,'gap%d'%gap,comp(r))
        prev=r
