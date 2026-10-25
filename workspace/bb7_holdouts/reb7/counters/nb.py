import idle, sys
from thr import rlg
from trace_check import expand
# NOBOUNDARY probe: tape = '101' + digits (10)^(4d+1) '1' ... + a=(10)^(4a+1) '1' + (10)^y + '00'
def tape(ds,a,y,pre='101'):
    return pre+''.join('10'*(4*d+1)+'1' for d in ds)+'10'*(4*a+1)+'1'+'10'*y
SS='00'
def moments(M,O,Q,ds,a,y,cnt=3,N=10**8,pre='101'):
    out=[]
    for l in rlg(M,O,Q,'10','1',SS,'P:'+tape(ds,a,y,pre)+' 0',N,4000,1):
        if l.startswith('H') or l.startswith('END') or l.startswith('TAPE'): out.append(l); break
        if l.count('|')<2: continue
        _,P,r=l.split('|',2); r=expand(r.split())
        if P.strip()!='-' or len(r)<3: continue
        if r[0]!=1 or r[-2]!=1 or r[-1]%2 or any(x%4!=1 for x in r[1:-1]): continue
        out.append((tuple((x-1)//4 for x in r[1:-2]),r[-1]))
        if len(out)>=cnt: break
    return out
if __name__=='__main__':
    M,O,Q=sys.argv[1:4]
    for line in sys.stdin:
        ds,a,y=line.split(';'); ds=eval(ds); a=int(a); y=int(y)
        print(ds,a,y,'->',moments(M,O,Q,ds,a,y,int(sys.argv[4]) if len(sys.argv)>4 else 3))
