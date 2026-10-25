import sys,re
from cyc import *
def pure(L):
    return re.fullmatch(r'(01)*',L) is not None or re.fullmatch(r'0?(10)*1',L) is not None
def cellstr(tape,lo,hi): return ''.join(str(tape.get(i,0)) for i in range(lo,hi))
def go(n,R,maxev=12,maxsteps=10**7,verbose=True):
    Ls='01'*n; Rs=R; st=0
    tape={}
    for i,c in enumerate(Ls): tape[i-len(Ls)]=int(c)
    for i,c in enumerate(Rs): tape[i]=int(c)
    pos=0;k=0
    ev=0
    while k<maxsteps and ev<maxev:
        e=T[(st,tape.get(pos,0))]
        if e is None: print('HALT',k); return
        w,d,ns=e; tape[pos]=w; pos+=d; st=ns; k+=1
        if ns==0:
            lo=min(tape); hi=max(tape)
            L=cellstr(tape,lo,pos); Rr=cellstr(tape,pos,hi+1).rstrip('0')
            if verbose: print(k,'L=',bl(L if len(L)%2==0 else '0'+L)[:100],'| R=',Rr[:80], len(Rr))
            ev+=1
if __name__=='__main__':
    go(int(sys.argv[1]),sys.argv[2],int(sys.argv[3]))
