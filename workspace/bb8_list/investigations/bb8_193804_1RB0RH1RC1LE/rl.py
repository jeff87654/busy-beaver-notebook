import sys
from sim import *
import re
def rle(tape,pos,q):
    s=show(tape,pos,q)
    # runs of 1 -> number, 0 runs -> 'z'*..; compress
    out=[]
    for m in re.finditer(r'\[[A-H]\]|1+|0+',s):
        t=m.group()
        if t[0]=='[': out.append(t)
        elif t[0]=='1': out.append('1^%d'%len(t) if len(t)>1 else '1')
        else: out.append('0^%d'%len(t) if len(t)>1 else '0')
    return ' '.join(out)
if __name__=='__main__':
    n=int(sys.argv[1])
    tape={};pos=0;q=0
    lo=hi=0
    ev=[]
    for i in range(n):
        b=tape.get(pos,0);e=T[(q,b)]
        if e is None: print('HALT',i);break
        w,d,nq=e
        tape[pos]=w;pos+=d;q=nq
        if pos>hi: hi=pos; ev.append((i,'R',q))
        if pos<lo: lo=pos; ev.append((i,'L',q))
    print(i,rle(tape,pos,q))
