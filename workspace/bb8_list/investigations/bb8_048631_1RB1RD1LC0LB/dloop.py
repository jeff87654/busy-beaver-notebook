import sys
from cyc import *
def trace(st0,Ls,Rs,maxsteps=400,stq='D',tailz='00'*3):
    tape={}
    for i,c in enumerate(Ls): tape[i-len(Ls)]=int(c)
    for i,c in enumerate(Rs+tailz): tape[i]=int(c)
    st='ABCDEFGH'.index(st0);pos=0
    for k in range(maxsteps):
        if 'ABCDEFGH'[st]==stq:
            lo=min(tape);hi=max(tape)
            print(k,''.join(str(tape.get(i,0)) for i in range(lo,pos)),'['+stq+']',''.join(str(tape.get(i,0)) for i in range(pos,hi+1)))
        e=T[(st,tape.get(pos,0))]
        if e is None: print('halt');return
        w,d,ns=e; tape[pos]=w;pos+=d;st=ns
if __name__=='__main__':
    trace(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),sys.argv[5])
