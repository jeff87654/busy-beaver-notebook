import random,sys
from run import events
from eng import step
from ev import rl
random.seed(int(sys.argv[1])); N=int(sys.argv[2])
bad=0; cnt={}
odd=lambda hi: random.randrange(1,hi,2)
for t in range(N):
    kind=random.choice('BBBTS')
    a=odd(random.choice([8,40,200]))
    if kind=='B':
        k=random.randint(1,16); c=[a]+[1]*k+[odd(random.choice([6,30,120]))+2]+[odd(random.choice([6,30])) for _ in range(random.randint(0,6))]
    elif kind=='T': c=[a]+[1]*random.randint(1,20)
    else: c=[odd(random.choice([10,60,300]))]
    nx,r=step(c)
    ev=events(c,10**9,1)
    got=ev[0][2] if ev and not isinstance(ev[0],str) else ev
    cnt[r[0]]=cnt.get(r[0],0)+1
    if got!=nx:
        bad+=1; print('MISS',rl(c),r,'got',(rl(got) if isinstance(got,list) else got),'pred',rl(nx))
print('tests',N,'miss',bad,sorted(cnt.items()))
