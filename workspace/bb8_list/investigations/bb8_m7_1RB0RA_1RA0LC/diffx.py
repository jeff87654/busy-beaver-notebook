from seqx import *
def window(pt,t):
    # common prefix / suffix removal
    i=0
    while i<min(len(pt),len(t)) and pt[i]==t[i]: i+=1
    j=0
    while j<min(len(pt),len(t))-i and pt[-1-j]==t[-1-j]: j+=1
    return i, pt[max(0,i-1):len(pt)-j], t[max(0,i-1):len(t)-j], j
if __name__=='__main__':
    n,b,N=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
    s=seq(n,b,N)
    prev=None
    for x in s:
        if isinstance(x,str): print(x); continue
        st,t,r=x
        if prev is not None:
            pt,pr=prev
            i,w1,w2,j=window(pt,t)
            print(st,'r %d->%d'%(pr,r),'pos %d'%i, rl(w1),'->',rl(w2),' (suffix kept %d)'%j)
        prev=(t,r)
