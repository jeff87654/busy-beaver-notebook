import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1]); lo_s=int(sys.argv[2]); hi_s=int(sys.argv[3])
out=[]
for step in range(n):
    s=tape.get(pos,0)
    if pos==-2 and q==7 and lo_s<=step<=hi_s:
        hi=max(k for k,v in tape.items() if v)
        st=''.join(str(tape.get(i,0)) for i in range(0,hi+1))
        rl=[(len(a),len(b)) for a,b in re.findall('(1+)(0*)',st)]
        k=0
        while k<len(rl) and rl[k]==(1,1): k+=1
        rest=rl[k:]
        if rest and rest[0][0]==2 and k>=1:
            a=k;g=rest[0][1]
            tt=[(y+1)//2 if y%2==1 else None for x,y in rest[1:]]
            std = (g==2*a+3)
            out.append((step,a,g,tt,std))
        else:
            out.append((step,None,None,rl,False))
    w,d,nq=T[(q,s)]
    tape[pos]=w
    pos+=1 if d=='R' else -1
    q=nq
    if step>hi_s: break
for o in out:
    if o[4]: print(o[0],'std (%d; %s)'%(o[1],','.join(map(str,o[3]))))
    elif o[1] is not None and o[1]>=2 : print(o[0],'  nonstd a=%d g=%d'%(o[1],o[2]),o[3])
