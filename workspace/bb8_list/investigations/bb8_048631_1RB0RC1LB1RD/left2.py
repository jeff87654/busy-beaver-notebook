import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1]); lo_s=int(sys.argv[2]); hi_s=int(sys.argv[3])
for step in range(n):
    s=tape.get(pos,0)
    if pos==-2 and q==7 and lo_s<=step<=hi_s:
        hi=max(k for k,v in tape.items() if v)
        st=''.join(str(tape.get(i,0)) for i in range(0,hi+1))
        rl=re.findall('(1+)(0*)',st)
        print(step,' '.join('%d.%d'%(len(a),len(b)) for a,b in rl))
    w,d,nq=T[(q,s)]
    tape[pos]=w
    pos+=1 if d=='R' else -1
    q=nq
    if step>hi_s: break
