import idle
from sim import T
# start: 0^inf 01 01 (10 11 01)^i A>00 0^inf ; run until K moment (A on 0 with 1 right, blank beyond)
for i in (1,2,3,4,5):
    cells=[0,1,0,1]+[1,0,1,1,0,1]*i+[0,0,1,1,1,1,1,1]
    tape={k:v for k,v in enumerate(cells)}; pos=len(cells)-8; q=0
    lo=0
    for s in range(1,2000):
        b=tape.get(pos,0); tr=T[(q,b)]
        if tr is None: print(i,"HALT at",s); break
        tape[pos]=tr[0]; pos+=tr[1]; q=tr[2]; lo=min(lo,pos)
        hi=max(tape)
        if q==0 and tape.get(pos,0)==0 and tape.get(pos+1,0)==1 and all(tape.get(j,0)==0 for j in range(pos+2,hi+1)):
            print(i,'steps',s,'minpos',lo,'cells left of head:',''.join(str(tape.get(j,0)) for j in range(0,pos)),'| head', pos, 'len0', len(cells))
            break
