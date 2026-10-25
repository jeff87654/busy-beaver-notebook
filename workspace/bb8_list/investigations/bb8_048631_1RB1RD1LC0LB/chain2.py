import sys
from cyc import *
def run_chain(n,R,it,lim=400,verbose=True,stopset='A'):
    Ls='01'*n; Rs=parse_blocks(R); st=0
    log=[]
    for i in range(it):
        r=run_from(Ls,Rs,st,maxsteps=10**8)
        kind,k,tape,pos,stt=r
        lo=min(tape); hi=max(tape)
        L=''.join(str(tape.get(i,0)) for i in range(lo,pos))
        if len(L)%2: L='0'+L
        Rr=''.join(str(tape.get(i,0)) for i in range(pos,hi+1))
        if len(Rr)%2: Rr+='0'
        if verbose: print(k,bl(L)[:120],'['+'ABCDEFGH'[stt]+']',bl(Rr)[:200])
        if kind!='stop': break
        Ls,Rs,st=L,Rr,stt
        if len(Ls)>lim*2: break
if __name__=='__main__':
    run_chain(int(sys.argv[1]),sys.argv[2],int(sys.argv[3]))
