import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
TM='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RF'
PRE='11'; SUF='101'
def kword(ds,a,b):
    w=PRE
    for d in ds: w+='01'*(3*d+1)+'1'
    w+='01'*(3*a+1)+'1'+'01'*(3*b+1)+SUF
    return w
def start(ds,a,b,tm=None):
    w=kword(ds,a,b)
    return Sim.from_word(tm or TM,'0000'+w+'0',4+len(w),'G')
def disp(s):
    t=s.tape; lo,hi=s.bounds()
    L=''.join(map(str,t[lo:s.pos])); R=''.join(map(str,t[s.pos+1:hi+1]))
    def rl(x):
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
if __name__=='__main__':
    ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); n=int(sys.argv[4])
    s=start(ds,a,b)
    print(s.show())
    for i in range(n):
        if not s.step(): print('HALT',s.steps,s.last); break
        if s.steps%int(sys.argv[5])==0: print(s.steps,disp(s))
