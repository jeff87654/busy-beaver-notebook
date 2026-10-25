from sim import *
import itertools,sys,re
def rle(s):
    return [(k,len(list(g))) for k,g in itertools.groupby(s)]
N=int(sys.argv[1])
tape={};pos=0;q=0;lo=0
prev=None
def parse(s):
    r=rle(s)
    # r[0]=('1',a) 
    a=r[0][1]
    if len(r)==1: return (a,)
    b=r[1][1]
    rest=r[2:]
    tail=rest
    # try (10)^m 1^5
    m=0;i=0
    while i+1<len(rest) and rest[i]==('1',1) and rest[i+1]==('0',1): m+=1;i+=2
    return (a,b,m,[(k,n) for k,n in rest[i:]])
lastkey=None
for st in range(N):
    t=T[(q,tape.get(pos,0))]
    if t is None: print("HALT",st);break
    tape[pos]=t[0]; pos+=1 if t[1]=='R' else -1; q=t[2]
    if pos<lo:
        lo=pos
        if q==3:
            L=min(tape);H=max(tape)
            s=''.join(str(tape.get(i,0)) for i in range(L,H+1))
            p=parse(s)
            if len(p)==1 or p[1]<=1 or p[0]==6 or p[1]==2:
                key=(p[1:] if len(p)>1 else p)
                # print only when b<=1 or a==6 (event boundaries)
                print(st,p if len(p)==1 else (p[0],p[1],p[2],p[3]))
