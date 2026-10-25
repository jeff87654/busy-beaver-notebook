import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
mx=0;last=0
n=int(sys.argv[1])
for step in range(n):
    s=tape.get(pos,0)
    w,d,nq=T[(q,s)]
    tape[pos]=w
    pos+=1 if d=='R' else -1
    q=nq
    if pos>mx:
        mx=pos
        if step+1-last>100:
            lo=min(tape)
            st=''.join(str(tape.get(i,0)) for i in range(lo,mx+1))
            runs=[len(x) for x in re.findall('1+',st)]
            print(step+1,'ABCDEFGH'[q],mx,st)
            print('   ',''.join(map(str,runs)))
        last=step+1
