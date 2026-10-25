import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1]); lo_s=int(sys.argv[2]); hi_s=int(sys.argv[3])
rets=[]
for step in range(n):
    s=tape.get(pos,0)
    if pos==-2 and q==7 and lo_s<=step<=hi_s:
        hi=max(k for k,v in tape.items() if v)
        st=''.join(str(tape.get(i,0)) for i in range(0,hi+1))
        rl=[(len(a),len(b)) for a,b in re.findall('(1+)(0*)',st)]
        rets.append((step,rl))
    w,d,nq=T[(q,s)]
    tape[pos]=w
    pos+=1 if d=='R' else -1
    q=nq
    if step>hi_s: break
for step,rl in rets:
    k=0
    while k<len(rl) and rl[k]==(1,1): k+=1
    rest=rl[k:]
    tot=sum(a+b for a,b in rl)
    if rest and rest[0][0]==2:
        a=k;g=rest[0][1]
        print(step,'T1 a=%d g=%d'%(a,g),'rest',[ (x,y) for x,y in rest[1:]],'tot',tot)
    else:
        print(step,'other',rl,'tot',tot)
