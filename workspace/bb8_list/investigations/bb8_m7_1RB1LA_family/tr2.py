import sys,re
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\neighbors_family_tools')
import os
from kd import *
from kfam import kstart
import kfam
from tmlit import ST
def rle(s):
    out=[];i=0
    while i<len(s):
        done=False
        for u in ('01','10'):
            j=i
            while s[j:j+2]==u: j+=2
            n=(j-i)//2
            if n>=3:
                out.append('(%s)^%d'%(u,n)); i=j; done=True; break
        if not done:
            out.append(s[i]); i+=1
    return ' '.join(out)
def trace(ds,a,b,mode='turn',maxsteps=100000,tm=TM):
    s=kstart(tm,ds,a,2*b+1,kfam.SHAPE)
    start=s.steps
    last_state=None
    lm=10**9
    prevdir=0
    prevpos=s.pos
    while s.steps-start<maxsteps:
        lo=s.lo;hi=s.hi
        n=s.steps-start
        show=False
        if mode=='all': show=True
        elif mode=='lmin':
            if s.pos<lm: lm=s.pos; show=True
        if show:
            w=''.join(str(x) for x in s.tape[lo:hi+1]); p=s.pos-lo
            print(n,ST[s.state],rle(w[:p])+' ['+w[p]+'] '+rle(w[p+1:]))
        prevpos=s.pos
        if not s.step(): print('HALT');break
        if mode=='turn':
            d=1 if s.pos>prevpos else -1
            if prevdir and d!=prevdir:
                w=''.join(str(x) for x in s.tape[s.lo:s.hi+1]); p=s.pos-s.lo
                print(n+1,ST[s.state],('<' if d<0 else '>'),rle(w[:p])+' ['+w[p]+'] '+rle(w[p+1:]))
            prevdir=d
        r=kfam.parse_at(s)
        if r is not None:
            print('K',r,'steps',s.steps-start);break
if __name__=='__main__':
    ds=tuple(int(x) for x in sys.argv[1].split(',') if x); a=int(sys.argv[2]); b=int(sys.argv[3])
    mode=sys.argv[4] if len(sys.argv)>4 else 'turn'
    trace(ds,a,b,mode)
