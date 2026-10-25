import sys
from tr import *
word=sys.argv[1]; maxs=int(sys.argv[2]); fac=float(sys.argv[3]) if len(sys.argv)>3 else 1.6
nxt=[1.0]
def show(st,q,p,tp,lo,hi):
    if q==1 and p>=hi and tp[p]==0 and tp[hi]==0 and st>=nxt[0]:
        nxt[0]=st*fac; return True
    return False
run(M,word,len(word),1,maxs,show)
