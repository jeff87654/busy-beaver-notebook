"""fol.py M WORD STEPS MAXEV [Q=B]: mirrored machine M, tape WORD (left->right), head on blank right of it, state Q.
At each event 'state Q on blank right of every 1' print step and generic parse: prefix | ds | a | b  (from the right:
S=1, (10)^(2b+1), 00, (10)^a, then (00 (10)^d)* greedily; leftover prefix printed). WORD may be 'K:ds:a:b' (P=101)."""
import idle, sys, re
from sim import parse
def kword(ds,a,b,P='101'):
    w=P
    for d in ds: w+='10'*d+'00'
    return w+'10'*a+'00'+'10'*(2*b+1)+'1'
def gparse(s):
    if not s.endswith('1'): return None
    i=len(s)-1
    k=0
    while i-2>=0 and s[i-2:i]=='10': i-=2; k+=1
    if k%2==0: return ('nb',s)
    b=(k-1)//2
    if s[i-2:i]!='00': return ('ns',s)
    i-=2
    blocks=[]
    while True:
        k=0
        while i-2>=0 and s[i-2:i]=='10': i-=2;k+=1
        blocks.append(k)
        if i-2>=0 and s[i-2:i]=='00' : 
            # ambiguous: 00 could be part of prefix; accept greedily
            i-=2; continue
        break
    a=blocks[0]; ds=blocks[1:][::-1]
    return (s[:i], ds, a, b)
def rle(ds):
    o=[];i=0
    while i<len(ds):
        j=i
        while j<len(ds) and ds[j]==ds[i]: j+=1
        o.append(str(ds[i])+('^%d'%(j-i) if j-i>1 else '')); i=j
    return '['+','.join(o)+']'
def follow(M,w,steps,maxev,Q=1,quiet=False):
    tr=parse(M)
    if w.startswith('K:'):
        _,ds,a,b=w.split(':'); ds=[int(x) for x in ds.split(',')] if ds else []
        w=kword(ds,int(a),int(b))
    T=bytearray(1<<22); off=1<<21
    for i,ch in enumerate(w): T[off+i]=ch=='1'
    p=off+len(w); q=Q; lo=off; hi=off+len(w)-1; ev=0; out=[]
    for st in range(steps):
        c=T[p]; t=tr[(q,c)]
        if t is None:
            out.append(('H',st,sum(T))); 
            if not quiet: print('HALT',st,'ones',sum(T))
            return out
        T[p]=t[0]
        if t[0]: lo=min(lo,p); hi=max(hi,p)
        p+=t[1]; q=t[2]
        if q==Q and T[p]==0 and p>hi:
            while hi>lo and not T[hi]: hi-=1
            if p>hi:
                while lo<hi and not T[lo]: lo+=1
                s=bytes(T[lo:hi+1]).replace(b'\x00',b'0').replace(b'\x01',b'1').decode()
                g=gparse(s)
                out.append((st+1,p-hi-1,g))
                if not quiet:
                    if g and len(g)==4: print(st+1,'gap',p-hi-1,'P=%s'%g[0][:60],rle(g[1]),g[2],g[3])
                    else: print(st+1,'gap',p-hi-1,'raw',s[:200])
                ev+=1
                if ev>=maxev: return out
    out.append(('T',steps)); 
    if not quiet: print('T')
    return out
if __name__=='__main__':
    M=sys.argv[1]; Q=ord(sys.argv[5])-65 if len(sys.argv)>5 else 1
    follow(M,sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),Q)
