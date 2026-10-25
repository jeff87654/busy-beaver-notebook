# literal: from 0^inf L [H]R 0^inf, run to next H event
from sim import T
import sys
def nexth(L,R,maxsteps=100000):
    tape={}
    for i,c in enumerate(L): tape[i-len(L)]=int(c)
    for i,c in enumerate(R): tape[i]=int(c)
    pos=0; st='H'; lo=hi=0; n=0
    while True:
        s=tape.get(pos,0); tr=T[(st,s)]
        if tr is None: return ('HALT',n,st,pos)
        tape[pos]=tr[0]; pos+=tr[1]; st=tr[2]; n+=1
        lo=min(lo,pos); hi=max(hi,pos)
        if st=='H': break
        if n>maxsteps: return ('LIMIT',n)
    a=min(min(tape),pos); b=max(max(tape),pos)
    s=''.join(str(tape.get(p,0)) for p in range(a,pos)); r=''.join(str(tape.get(p,0)) for p in range(pos,b+1))
    return ('H',n,s.lstrip('0') if True else s, r.rstrip('0'), pos, lo, hi)
if __name__=="__main__":
    print(nexth(sys.argv[1],sys.argv[2]))
