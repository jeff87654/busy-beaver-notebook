from lit import *
import sys
def build(L,x,y):
    cells=[1]*L+[0]+[1]*x+[0]+[1]*y
    tape={i:1 for i,c in enumerate(cells) if c}
    return tape,len(cells)+2,3
def blocks(tape):
    lo=min(tape);hi=max(tape)
    s="".join(str(tape.get(i,0)) for i in range(lo,hi+1))
    return tuple(len(b) for b in s.split("0")),lo
def step(L,x,y,maxn=10**7):
    tape,p,q=build(L,x,y);hi=p-1;n=0
    while n<maxn:
        if p>hi:
            hi=p
            if n>0 and q==3 and p==max(tape)+3 and len(blocks(tape)[0])==3:
                b,lo=blocks(tape)
                return n,b,lo
        r=T[(q,tape.get(p,0))]
        if r is None: return n,"HALT",("ABCDEFGH"[q],p)
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns;n+=1
    return None
if __name__=="__main__":
    for L in [3,8,13,28,2,1]:
        for x in [1,3,5,7]:
            for y in [3,11,19,4,5]:
                print(L,x,y,step(L,x,y))
