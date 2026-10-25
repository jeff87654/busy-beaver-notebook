import sys
from sim0 import parse
TM=sys.argv[1]
d=parse(TM)
def run(word, N=100000, q=1):
    """word: tape string with head at position len(word) (blank right), state q (B=1)"""
    tape={i:int(c) for i,c in enumerate(word)}
    pos=len(word); n=0
    dirs=None
    out=[]
    lo=min(tape); hi=max(tape)
    prevdir=None
    while n<N:
        s=tape.get(pos,0)
        t=d[(q,s)]
        if t is None: out.append((n,'HALT')); break
        w,dr,nq=t
        tape[pos]=w
        newdir=1 if dr=='R' else -1
        if prevdir is not None and newdir!=prevdir:
            out.append((n,pos,'ABCDEFGH'[q],dict(tape)))
        prevdir=newdir
        pos+=newdir; q=nq; n+=1
    return out
def tstr(tape,pos=None):
    lo=min(tape); hi=max(tape)
    return ''.join(str(tape.get(i,0)) for i in range(lo,hi+1)),lo
if __name__=='__main__':
    c=int(sys.argv[2])
    word='10'*(2*c+1)+'011'
    # R4: all zero list a=0
    word='0'+word
    ev=run(word,N=int(sys.argv[3]) if len(sys.argv)>3 else 3000)
    for e in ev[:int(sys.argv[4]) if len(sys.argv)>4 else 80]:
        if e[1]=='HALT' or isinstance(e[1],str): print(e); continue
        n,pos,q,tape=e
        s,lo=tstr(tape)
        print(n,q,pos-lo,s)
