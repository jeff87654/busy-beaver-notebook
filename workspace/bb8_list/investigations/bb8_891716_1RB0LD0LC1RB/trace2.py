import sys
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
import os
os.environ['BB_KENC']='10,0'
from kfam import kword, set_shape
set_shape("B","011")
from sim0 import parse
TM=os.environ.get('TM',"1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
d=parse(TM)
def run(W,b,N=100000,every=None,stop_at_K=False):
    ds=tuple(reversed(W[1:])); a=W[0]
    word=kword(ds,a,2*b+1)
    tape={i:int(c) for i,c in enumerate(word)}
    pos=len(word); q=1; n=0
    lo0=0
    hist=[]
    while n<N:
        s=tape.get(pos,0)
        t=d[(q,s)]
        if t is None: print('HALT',n); return hist
        w,dr,nq=t
        tape[pos]=w
        pos+= 1 if dr=='R' else -1
        q=nq; n+=1
        hist.append((n,q,pos,dict(tape)))
        if stop_at_K and q==1 and pos>=max(k for k,v in tape.items() if v)+1 and tape.get(pos-1)==1 and tape.get(pos-2)==1 and tape.get(pos-3)==0 and n>5 :
            # K event? check suffix 011 at head
            break
    return hist
def show(tape,pos,q):
    lo=min(min(tape),pos); hi=max(max(tape),pos)
    s=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
    return s[:pos-lo]+'['+'ABCDEFGH'[q]+']'+s[pos-lo:]
if __name__=='__main__':
    W=[int(x) for x in sys.argv[1].split(',')] if sys.argv[1] else []
    b=int(sys.argv[2])
    h=run(W,b,N=int(sys.argv[3]))
    sel=sys.argv[4] if len(sys.argv)>4 else 'x'
    for n,q,pos,tape in h:
        # print when head moves to a new leftmost position (leftmost record)
        pass
    lm=10**9
    for n,q,pos,tape in h:
        if pos<lm:
            lm=pos
            print(n,show(tape,pos,q))
    print('total',len(h))
    # snapshots at right-turn events from state D/E at the leftmost nonblank
    print('--- all steps in states where head is left of position of first b-cell')
