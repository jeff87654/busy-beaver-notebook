from seqx import *
import sys
def kseqS(n,b,N,maxprint=100000,skip=0):
    return seq(n,b,N,maxprint,skip,tail='111001')
def isR1(pt,pr,t,r):
    return len(pt)==len(t) and pt[:-1]==t[:-1] and pt[-1]-3==t[-1] and r==2*pr+4
if __name__=='__main__':
    n,b,N=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
    prev=None
    for x in kseqS(n,b,N):
        if isinstance(x,str): print(x); continue
        st,t,r=x
        if prev is not None and isR1(prev[0],prev[1],t,r): prev=(t,r); continue
        print(st,rl(t),r); prev=(t,r)
