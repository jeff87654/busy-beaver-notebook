from common import *
import sys
def show_tr(ds,a,b,maxn=100,tm=MIR):
    s = kstart(tm,ds,a,b)
    n=0
    while n<maxn:
        lo=s.lo; hi=s.hi
        seg=''.join(map(str,s.tape[lo-2:hi+3]))
        p=s.pos-(lo-2)
        print('%3d %s %s'%(s.steps,ST[s.state],seg[:p]+'['+seg[p]+']'+seg[p+1:]))
        if not s.step(): print('HALT');break
        n+=1
        if n>0 and parse_at(s) is not None:
            lo=s.lo; hi=s.hi
            print('K',parse_at(s)); break
if __name__=='__main__':
    ds=tuple(int(x) for x in sys.argv[1].split(',') if x); show_tr(ds,int(sys.argv[2]),int(sys.argv[3]))
