import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
import tr
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); N=int(sys.argv[4])
s=tr.start(ds,a,b)
def cmp(x):
    out=[];i=0
    while i<len(x):
        best=None
        for u in ('01','10','011','110','101','0','1'):
            k=0
            while x.startswith(u,i+len(u)*k): k+=1
            if (k>=3 and len(u)>1) or (k>=4 and len(u)==1):
                if best is None or k*len(u)>best[0]*len(best[1]): best=(k,u)
        if best: out.append('(%s)^%d'%(best[1],best[0])); i+=best[0]*len(best[1])
        else: out.append(x[i]); i+=1
    return ' '.join(out)
while s.steps<N:
    if not s.step(): print('HALT');break
    if ST[s.state]=='G' and s.tape[s.pos]==0:
        t=s.tape; lo,hi=s.bounds()
        if hi<=s.pos:
            print(s.steps, cmp(''.join(map(str,t[lo:s.pos]))))
