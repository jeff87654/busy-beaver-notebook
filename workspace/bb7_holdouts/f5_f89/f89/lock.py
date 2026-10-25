# lock.py : read kl U=01 'a' output from stdin, check every consecutive pair of p1 events (odd configs) against eng.step
import sys
from ev import parse, rl
from eng import step
prev=None; n=0; bad=0; cnt={}; last=None; first=None
for line in sys.stdin:
    p=line.split()
    if not p or not p[0].isdigit(): print(line.strip()); continue
    pre,d=parse(p[1:])
    if pre!=1: continue
    if prev is not None:
        nx,r=step(prev)
        if r=='EVEN': pass
        else:
            n+=1; cnt[r[0]]=cnt.get(r[0],0)+1
            if nx!=d:
                bad+=1
                if bad<10: print('MISS',p[0],r,rl(prev),'->',rl(d),'pred',rl(nx))
    if d and all(x%2 for x in d) and first is None: first=(p[0],rl(d))
    prev=d; last=(p[0],len(d),max(d))
print('checked',n,'miss',bad,'rules',cnt,'first odd',first,'last step,len,max',last)
