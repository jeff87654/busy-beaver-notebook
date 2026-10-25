import sys
from kd import *
from kfam import kstart
def seq(ds,a,b,n=8,N=10**6):
    s=kstart(TM,ds,a,2*b+1,kfam.SHAPE)
    out=[]
    last=s.steps
    for i in range(n):
        r=run_from(s,N)
        if r[0]!='K':
            out.append(r[:3]); break
        d,aa,bu=r[2]
        out.append(('K',d,aa,'b=%s'%((bu-1)/2),'+%d'%(r[1]-last))); last=r[1]
    return out
if __name__=='__main__':
    ds=tuple(int(x) for x in sys.argv[1].split(',') if x); a=int(sys.argv[2]); b=int(sys.argv[3]); n=int(sys.argv[4]) if len(sys.argv)>4 else 6
    print('start',ds,a,b)
    for o in seq(ds,a,b,n): print(o)
