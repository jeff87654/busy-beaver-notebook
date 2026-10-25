import random,sys
from run import events
from eng import step
from ev import rl
random.seed(int(sys.argv[1])); N=int(sys.argv[2])
bad=0; cnt={}
for t in range(N):
    L=random.randint(1,14)
    c=[random.choice([1,1,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]) for _ in range(L)]
    if random.random()<0.3: c[0]=random.randrange(1,60,2)
    nx,r=step(c)
    ev=events(c,10**8,1)
    got=ev[0][2] if ev and not isinstance(ev[0],str) else ev
    cnt[r]=cnt.get(r,0)+1
    if got!=nx:
        bad+=1; print('MISS',rl(c),r,'got',(rl(got) if isinstance(got,list) else got),'pred',rl(nx))
print('tests',N,'miss',bad,sorted(cnt.items()))
