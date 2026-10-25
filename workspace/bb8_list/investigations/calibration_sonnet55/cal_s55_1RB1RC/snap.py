from sim import *
import itertools
def rle(s):
    return ' '.join(f"{k}^{len(list(g))}" for k,g in itertools.groupby(s))
tape={};pos=0;q=0;lo=0
cnt=0
for st in range(200000):
    t=T[(q,tape.get(pos,0))]
    if t is None: print("HALT",st);break
    tape[pos]=t[0]; pos+=1 if t[1]=='R' else -1; q=t[2]
    if pos<lo:
        lo=pos
        if q==3 and cnt<40 and st>100:
            cnt+=1
            L=min(tape);H=max(tape)
            s=''.join(str(tape.get(i,0)) for i in range(L,H+1))
            print(st,'D at',pos-L,rle(s))
