import sys,re
from cyc import *
def cellstr(tape,lo,hi): return ''.join(str(tape.get(i,0)) for i in range(lo,hi))
def rlb(s):
    # block form of R string (cells), 2-blocks, strip trailing 0s
    s=s.rstrip('0')
    if len(s)%2: s+='0'
    return bl(s)
def go(n,Rblocks,maxev=40,maxsteps=10**8,show=True,tailz=40):
    Rs=parse_blocks(Rblocks)+'0'*tailz
    tape={}
    for i,c in enumerate('01'*n): tape[i-2*n]=int(c)
    for i,c in enumerate(Rs): tape[i]=int(c)
    st=0;pos=0;k=0;ev=0;out=[]
    while k<maxsteps and ev<maxev:
        e=T[(st,tape.get(pos,0))]
        if e is None: 
            if show: print('HALT',k)
            out.append('HALT');break
        w,d,ns=e; tape[pos]=w; pos+=d; st=ns; k+=1
        if ns==0:
            lo=min(tape); hi=max(tape)
            L=cellstr(tape,lo,pos); Rr=cellstr(tape,pos,hi+1)
            if len(L)%2: L='0'+L
            out.append((k,L,Rr))
            if show: print(k,bl(L)[:70],'|',rlb(Rr)[:150])
            ev+=1
    return out
if __name__=='__main__':
    go(int(sys.argv[1]),sys.argv[2],int(sys.argv[3]))
