import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1]); Q=sys.argv[2]; lim=int(sys.argv[3])
hi=-1;cnt=0;last=0
for step in range(n):
    s=tape.get(pos,0)
    if 'ABCDEFGH'[q]==Q and pos>hi and s==0:
        lo=min(tape)
        st=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
        runs=[len(x) for x in re.findall('1+',st)]
        cnt+=1
        if cnt<=lim: print(step,pos,hi,'|',st,'|',runs, '+%d'%(step-last))
        last=step
    w,d,nq=T[(q,s)]
    tape[pos]=w
    if w: hi=max(hi,pos)
    pos+=1 if d=='R' else -1
    q=nq
