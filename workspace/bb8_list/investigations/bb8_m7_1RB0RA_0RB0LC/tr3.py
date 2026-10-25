import sys
from tr import *
word=sys.argv[1]; lo_s=int(sys.argv[2]); hi_s=int(sys.argv[3]); 
def show(st,q,p,tp,lo,hi):
    return st>=lo_s and q==1 and p>=hi and tp[p]==0 and tp[hi]==0
run(M,word,len(word),1,hi_s,show)
