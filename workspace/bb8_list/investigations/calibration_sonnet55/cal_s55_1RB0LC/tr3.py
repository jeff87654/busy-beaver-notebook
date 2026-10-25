import sys,re
from tr2 import *
def canon(s):
    # compress repeated (0 1) and (1 0) alternating patterns
    s=re.sub(r'((?:0 1 ){3,})',lambda m:'(01)^%d '%(len(m.group(1))//4),s+' ')
    s=re.sub(r'((?:1 0 ){3,})',lambda m:'(10)^%d '%(len(m.group(1))//4),s)
    return s.strip()
if __name__=="__main__":
    n=int(sys.argv[1]);t1=int(sys.argv[2]);st=sys.argv[3]
    prev=None
    for t,s in trace(n,0,t1,st):
        c=canon(s); sh=re.sub(r'\d+','#',c)
        if sh!=prev: print(t,c)
        prev=sh
