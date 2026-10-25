import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
from tr import TM, start
from fam import parse
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); lo_s=int(sys.argv[4]); hi_s=int(sys.argv[5])
s=start(ds,a,b)
def disp(s):
    t=s.tape; lo,hi=s.bounds()
    L=''.join(map(str,t[lo:s.pos])); R=''.join(map(str,t[s.pos+1:hi+1]))
    import re
    def rl(x):
        # greedy compress (01)^k and (10)^k
        out=[];i=0
        while i<len(x):
            for u in ('01','10'):
                k=0
                while x.startswith(u,i+2*k): k+=1
                if k>=3:
                    out.append('(%s)^%d'%(u,k)); i+=2*k; break
            else:
                out.append(x[i]); i+=1
        return ' '.join(out)
    return '%s <%s%d> %s'%(rl(L),ST[s.state],t[s.pos],rl(R))
prevd=0
while s.steps<hi_s:
    q=s.state; p0=s.pos
    if not s.step(): print('HALT'); break
    d=s.pos-p0
    if s.steps>=lo_s and d!=prevd:
        print(s.steps,disp(s))
    prevd=d
