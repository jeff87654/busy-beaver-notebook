# positive control: find a tape family pre (w)^n post with head state Q that halts literally for n=4..9, then let msim
# (symbolic n) decide it: it must report HALT.
import random, itertools
from msim import *
T=parse(M)
def lit(tape,h,q,maxs=5000):
    tape=list(tape)
    for st in range(maxs):
        tr=T[(q,tape[h])]
        if tr is None: return st
        tape[h]=tr[0]; h+=tr[1]; q=tr[2]
        if h<0: tape.insert(0,'0'); h=0
        if h>=len(tape): tape.append('0')
    return None
random.seed(7); found=0
for trial in range(200000):
    pre=''.join(random.choice('01') for _ in range(random.randint(0,4)))
    w=random.choice(['01','10','011','101','110','1','111'])
    post=''.join(random.choice('01') for _ in range(random.randint(1,4)))
    q=random.choice('ABCDEFG')
    hs=[lit('0'+pre+w*n+post+'0',0,q) for n in range(4,10)]
    if all(x is not None for x in hs) and all(hs[i+1]>hs[i] for i in range(5)):
        n=V('n',4)
        items=['0']+list(pre)+[['B',w,n]]+list(post)+['0']
        try:
            s=Sim(items,0,q); ev=s.run(lambda e,S: False, 10**5)
            print('family [%s]0 %s (%s)^n %s 0 : literal halt steps n=4..9 %s ; msim symbolic n>=4: %s'%(q,pre,w,post,hs,ev))
        except Fail as e: found-=1
        found+=1
        if found>=3: break
