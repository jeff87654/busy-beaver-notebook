from lit import *
import itertools,sys
def rl(s): return " ".join(f"{k}^{len(list(g))}" if k in "01" else k for k,g in itertools.groupby(s))
def runfrom(tape,p,q,N,ev_states="A"):
    out=[]
    for n in range(N):
        if q==0 and "A" in ev_states: out.append((n,rl(render(tape,p,q))))
        r=T[(q,tape.get(p,0))]
        if r is None: out.append((n,"HALT "+rl(render(tape,p,q)))); break
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns
    return out
def Q(k,m,L=3):
    tape={}
    for i in range(L): tape[i]=1
    p=L
    for i in range(k): tape[p+1+i]=1   # A at p; cell p is 1? 
    return tape,p
def mk(L,k,m):
    tape={};p=L
    for i in range(L): tape[i]=1
    for i in range(k): tape[L+i]=1
    for i in range(m): tape[L+k+2+i]=1
    return tape,p
if __name__=="__main__":
    L,k,m,N=map(int,sys.argv[1:5])
    t,p=mk(L,k,m)
    for n,s in runfrom(t,p,0,N): print(n,s)
