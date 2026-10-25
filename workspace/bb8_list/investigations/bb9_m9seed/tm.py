# minimal literal TM simulator utilities (bb9_m9seed)
from collections import defaultdict
def parse(s):
    rows=s.split('_'); t={}
    for q,r in enumerate(rows):
        for c in range(2):
            x=r[3*c:3*c+3]
            if x[2] in '-ZH' and (x=='---' or x[2]=='Z' or (x[2]=='H' and len(rows)<8)):
                t[(q,c)]=None
            else:
                nx=ord(x[2])-65
                t[(q,c)]=None if nx>=len(rows) else (int(x[0]),1 if x[1]=='R' else -1,nx)
    return t,len(rows)
def run(tm,tape=None,pos=0,q=0,maxs=10**7,usage=None,cb=None):
    T=defaultdict(int)
    if tape:
        for i,v in enumerate(tape): T[i]=v
    s=0
    while s<maxs:
        c=T[pos]; tr=tm[(q,c)]
        if usage is not None: usage[(q,c)]+=1
        if tr is None: return ('HALT',s+1,T,pos,q)
        w,d,nx=tr; T[pos]=w; pos+=d; q=nx; s+=1
        if cb and cb(T,pos,q,s): return ('CB',s,T,pos,q)
    return ('RUN',s,T,pos,q)
def show(T,pos,q,lo=None,hi=None):
    ks=[k for k,v in T.items() if v] or [pos]
    lo=min(ks+[pos]) if lo is None else lo; hi=max(ks+[pos]) if hi is None else hi
    out=''
    for i in range(lo,hi+1):
        out+=('[%s%d]'%(chr(65+q),T[i])) if i==pos else str(T[i])
    return out
