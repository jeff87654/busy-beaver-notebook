from probe import Sim
from rewrite import Rope,advance
import random

def check(a,parts):
    tail=Rope(parts);raw=tail.string()
    s=Sim(1,'0000'+'100'*a+raw,6)
    na,nt,dt,r=advance(a,tail)
    for _ in range(dt):
        if s.steps>=dt or s.halted:break
        s.step()
    if na is None:
        if not s.halted:s.step()
        assert s.halted and s.steps==dt,('HALT',a,raw,dt,s.steps)
    else:
        expect=('0000'+'100'*na+nt.string()).rstrip('0')
        got=s.word().rstrip('0')
        assert (s.steps,s.q,s.L,s.cur)==(dt,6,[],0) and got==expect,(r,a,raw,dt,s.steps,na,nt,s.q,s.summary(),expect)
    return r

if __name__=='__main__':
    rng=random.Random(231)
    count=0
    for a in range(2,10):
        for j in range(64):
            if j<4:continue
            check(a,[(f'{j:06b}'+'1100101001',1)])
            count+=1
    print(count,'prefix checks passed')
    count=0
    for a in range(2,12):
        for n in range(1,12):
            for p in ('010','110','001','1100'):
                check(a,[(p,n),('101001',1)])
                count+=1
    print(count,'repeated-pattern checks passed')
    check(8,[])
    print('blank reset check passed')
