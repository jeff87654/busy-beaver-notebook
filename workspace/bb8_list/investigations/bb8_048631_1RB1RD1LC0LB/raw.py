import sys
from cyc import *
n=int(sys.argv[1]); R=sys.argv[2]; it=int(sys.argv[3])
Ls='01'*n; Rs=parse_blocks(R); st=0
import re
def rl(s): return ' '.join(f'{m.group(0)[0]}^{len(m.group(0))}' if len(m.group(0))>1 else m.group(0)[0] for m in re.finditer(r'0+|1+',s))
for i in range(it):
    r=run_from(Ls,Rs,st,maxsteps=10**8)
    kind,k,tape,pos,stt=r
    lo=min(tape); hi=max(tape)
    L=''.join(str(tape.get(i,0)) for i in range(lo,pos)); Rr=''.join(str(tape.get(i,0)) for i in range(pos,hi+1))
    print(k,len(L),'|'+Rr, '   L-end',L[:30].replace('','')[:0]+rl(L[:12])+'...'+rl(L[-6:]))
    if kind!='stop': break
    Ls,Rs,st=L,Rr,stt
    if len(Ls)>2000: break
