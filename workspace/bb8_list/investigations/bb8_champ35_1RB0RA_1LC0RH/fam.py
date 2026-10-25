import sys,re
sys.path.insert(0,'.')
from tmlit import Sim, ST
from tr import TM, start, kword
def parse(s):
    """if s is in K shape return (ds,a,b) else None"""
    if ST[s.state]!='G' or s.tape[s.pos]!=0: return None
    t=s.tape; lo,hi=s.bounds()
    if hi>s.pos: return None
    w=''.join(map(str,t[lo:s.pos]))
    if not w.endswith('10101') or not w.startswith('1'): return None
    w=w[1:-5]
    # w = (01)^(3d+1) 1 ... (01)^(3a+1) 1 (01)^(3b+1)
    # parse from right: b run
    out=[]
    def runs(w):
        r=[]
        while True:
            k=0
            while w.endswith('01'): w=w[:-2]; k+=1
            if k==0 or (k-1)%3: return None
            r.append((k-1)//3)
            if w=='': return r
            if not w.endswith('1'): return None
            w=w[:-1]
    r=runs(w)
    if r is None: return None
    r.reverse()  # farthest first: ds..., a, b
    if len(r)<2: return None
    return (r[:-2], r[-2], r[-1])
def run_next(ds,a,b,N=10**7):
    s=start(ds,a,b)
    n0=0
    while s.steps<N:
        if not s.step(): return ('HALT',s.steps,s.last)
        p=parse(s)
        if p is not None: return ('K',s.steps,p)
    return ('TIMEOUT',s.steps)
if __name__=='__main__':
    ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
    print(run_next(ds,a,b))
