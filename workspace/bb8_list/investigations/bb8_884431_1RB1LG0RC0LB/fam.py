"""Family K(ds; a; b) of the actual machine (head at the LEFT end):
   0^inf B> 0 0 (11)^b 0 (11)^a 0 (11)^dn 0 ... 0 (11)^d1 1 0^inf     ds=[d1..dn] (d1 farthest from the head)
"""
from sim8 import *
def kword(ds,a,b):
    w='00'+'11'*b+'0'+'11'*a
    for d in reversed(ds):
        w+='0'+'11'*d
    w+='1'
    return w
def kstart(ds,a,b):
    w=kword(ds,a,b)
    return M('0'+w,0,'B')   # head on the blank before the word
def parse_k(m):
    """If m is in family shape return (ds,a,b) else None. Head must be in B on a blank with all left of head blank."""
    if m.q!=1: return None
    t=m.t; p=m.p
    if t[p]!=0: return None
    if any(t[:p]): return None
    i=p+1
    # find end
    hi=len(t)-1
    while hi>p and t[hi]==0: hi-=1
    w=''.join(map(str,t[p+1:hi+1]))
    if not w.startswith('00'): return None
    w=w[2:]
    # parse: runs of 11 separated by single 0; last token prefix 1
    if not w.endswith('1'): return None
    w=w[:-1]            # remove prefix 1  -> '11'*b 0 '11'*a 0 ...
    # now w = (11)^b 0 (11)^a 0 (11)^dn ... 0 (11)^d1   ; split by '0' but runs may be empty (adjacent zeros)
    parts=w.split('0')
    # careful: 'a 0 0' => empty parts ; split on single 0 gives exact runs since separators are single 0
    runs=[]
    for x in parts:
        if set(x)-{'1'}: return None
        if len(x)%2: return None
        runs.append(len(x)//2)
    if len(runs)<2: return None
    b=runs[0]; a=runs[1]; ds=list(reversed(runs[2:]))
    return (tuple(ds),a,b)
def run_next(ds,a,b,N=10**6,start_check=True):
    m=kstart(ds,a,b)
    while m.n<N:
        if not m.step(): return ('HALT',m.n,(ST[m.q],m.t[m.p]),m)
        r=parse_k(m)
        if r is not None and m.n>0: return ('K',m.n,r)
    return ('TIMEOUT',m.n)
if __name__=='__main__':
    import sys
    m=kstart([2,1,1],0,4); print(parse_k(m), kword([2,1,1],0,4))
    print(run_next([2,1,1],0,4))
