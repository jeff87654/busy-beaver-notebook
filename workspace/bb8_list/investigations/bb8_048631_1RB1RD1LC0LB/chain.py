import sys
from cyc import *
n=int(sys.argv[1]); R=sys.argv[2]; it=int(sys.argv[3])
Ls='01'*n; Rs=parse_blocks(R)
st=0
for i in range(it):
    r=run_from(Ls,Rs,st,maxsteps=3*10**7)
    print(fmt(r)[:250])
    kind,k,tape,pos,stt=r
    if kind!='stop': break
    lo=min(tape); hi=max(tape)
    Ls=''.join(str(tape.get(i,0)) for i in range(lo,pos)); 
    if len(Ls)%2: Ls='0'+Ls
    Rs=''.join(str(tape.get(i,0)) for i in range(pos,hi+1))
    st=stt
    if len(Ls)>3000: break
