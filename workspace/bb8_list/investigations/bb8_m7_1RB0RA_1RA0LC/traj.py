from xg import *
from seqx import rl
import sys
# trajectory from tokens/r with tail 0S; print only borrow events (non X1 steps)
def traj(toks,r,N=200000000,maxprint=100000,P=True):
    res=litx(toks,r,P,N=N,maxprint=maxprint)
    prev=(toks,r)
    out=[]
    for x in res:
        if isinstance(x,str): out.append(x); continue
        st,t,rr=x
        pt,pr=prev
        if len(pt)==len(t) and pt[:-1]==t[:-1] and pt[-1]-1==t[-1] and rr==pr+2:
            prev=(t,rr); continue
        out.append((st,pt,pr,t,rr)); prev=(t,rr)
    return out
if __name__=='__main__':
    toks=eval(sys.argv[1]); r=int(sys.argv[2]); N=int(sys.argv[3])
    for e in traj(toks,r,N):
        if isinstance(e,str): print(e); continue
        st,pt,pr,t,rr=e
        print(st, rl(pt),pr,'->',rl(t),rr)
