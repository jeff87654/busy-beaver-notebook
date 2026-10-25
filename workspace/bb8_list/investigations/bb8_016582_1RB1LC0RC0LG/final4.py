from rules import *
def halt_run(L,x,y):
    tape,p,q=build(L,x,y);n=0
    while True:
        r=T[(q,tape.get(p,0))]
        if r is None: return n,sum(tape.values()),"ABCDEFGH"[q],tape.get(p,0),p,min(tape),max(tape)
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns;n+=1
for y in [3,4,5,6,7,8,11,19,27]:
    print(y,halt_run(4,1,y))
