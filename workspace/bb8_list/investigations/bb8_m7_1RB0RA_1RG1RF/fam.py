import sys,re
sys.path.insert(0,'.')
from tmlit import Sim, ST
import tr
def parse(s):
    """if s is in K shape return (ds,a,b) else None. K = 11 (01)^(3d+1) 1 ... (01)^(3a+1) 1 (01)^(3b+1) 101 G> (blank right)"""
    if ST[s.state]!='G' or s.tape[s.pos]!=0: return None
    t=s.tape; lo,hi=s.bounds()
    if hi>s.pos: return None
    w=''.join(map(str,t[lo:s.pos]))
    if not w.endswith(tr.SUF) or not w.startswith(tr.PRE): return None
    w=w[len(tr.PRE):-len(tr.SUF)]
    r=[]
    while True:
        k=0
        while w.endswith('01'): w=w[:-2]; k+=1
        if k==0 or (k-1)%3: return None
        r.append((k-1)//3)
        if w=='': break
        if not w.endswith('1'): return None
        w=w[:-1]
    r.reverse()
    if len(r)<2: return None
    return (r[:-2], r[-2], r[-1])
def run_next(ds,a,b,N=10**7,tm=None):
    s=tr.start(ds,a,b,tm)
    while s.steps<N:
        if not s.step(): return ('HALT',s.steps,s.last)
        p=parse(s)
        if p is not None: return ('K',s.steps,p)
    return ('TIMEOUT',s.steps)
if __name__=='__main__':
    ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
    print(run_next(ds,a,b))
