import sys, itertools
from cyc import *
blocks=['00','01','10','11']
def cycle(n,Rs,maxsteps=2*10**6):
    tape={}
    Ls='01'*n
    for i,c in enumerate(Ls): tape[i-len(Ls)]=int(c)
    for i,c in enumerate(Rs): tape[i]=int(c)
    pos=0;st=0;k=0;reach=0
    while k<maxsteps:
        e=T[(st,tape.get(pos,0))]
        if e is None: return ('halt',k,None,reach)
        w,d,ns=e; tape[pos]=w; pos+=d; st=ns; k+=1
        reach=max(reach,pos)
        if ns==0:
            lo=min(tape); hi=max(tape)
            L=''.join(str(tape.get(i,0)) for i in range(lo,pos))
            R=''.join(str(tape.get(i,0)) for i in range(pos,hi+1))
            return ('stop',k,(L,R,pos),reach)
    return ('max',k,None,reach)
if __name__=='__main__':
    n=int(sys.argv[1]); L=int(sys.argv[2])
    for combo in itertools.product(blocks,repeat=L):
        pre=''.join(combo)
        Rs=pre+'0'*40   # tail zeros
        kind,k,res,reach=cycle(n,Rs)
        if kind!='stop': print(' '.join(combo),kind,k,'reach',reach); continue
        Lr,Rr,pos=res
        # compress
        Lb=Lr; 
        if len(Lb)%2: Lb='0'+Lb
        Rb=Rr
        if len(Rb)%2: Rb+='0'
        print(' '.join(combo),'->',k,bl(Lb)[:60],'[A]',bl(Rb)[:100].replace(' 00^','  00^'),'reach',reach)
