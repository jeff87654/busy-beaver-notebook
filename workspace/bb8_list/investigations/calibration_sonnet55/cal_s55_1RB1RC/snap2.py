from sim import *
import itertools,sys
def rle(s):
    return ' '.join(f"{k}^{len(list(g))}" for k,g in itertools.groupby(s))
N=int(sys.argv[1])
tape={};pos=0;q=0;lo=0
prev=None
for st in range(N):
    t=T[(q,tape.get(pos,0))]
    if t is None: print("HALT",st);break
    tape[pos]=t[0]; pos+=1 if t[1]=='R' else -1; q=t[2]
    if pos<lo:
        lo=pos
        if q==3:
            L=min(tape);H=max(tape)
            s=''.join(str(tape.get(i,0)) for i in range(L,H+1))
            r=rle(s).split(' ')
            key=' '.join(r[2:])
            if key!=prev:
                print(st,rle(s)); prev=key
            # rest-of-tape key changes
