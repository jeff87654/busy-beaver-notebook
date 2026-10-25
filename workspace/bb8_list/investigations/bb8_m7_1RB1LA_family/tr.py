import sys
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\neighbors_family_tools')
from kd import *
from kfam import kstart
import kfam
from tmlit import ST
def trace(ds,a,b,n=None,every=1,show_from=0,maxsteps=100000):
    s=kstart(TM,ds,a,2*b+1,kfam.SHAPE)
    out=[]
    last=s.steps
    k=0
    while s.steps-last<maxsteps:
        if s.steps-last>=show_from and (s.steps-last)%every==0:
            lo=s.lo;hi=s.hi
            w=''.join(str(x) for x in s.tape[lo:hi+1])
            p=s.pos-lo
            print(s.steps-last,ST[s.state],w[:p]+'['+w[p]+']'+w[p+1:])
        if not s.step(): print('HALT');break
        r=kfam.parse_at(s)
        if r is not None:
            print('K',r);break
if __name__=='__main__':
    ds=tuple(int(x) for x in sys.argv[1].split(',') if x); a=int(sys.argv[2]); b=int(sys.argv[3])
    trace(ds,a,b)
