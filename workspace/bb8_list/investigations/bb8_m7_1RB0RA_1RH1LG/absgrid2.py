import sys,random
from absgrid import *
random.seed(int(sys.argv[1])); n=int(sys.argv[2]); bad=0; cnt=0; used=0
for it in range(n):
    L=random.randint(1,6)
    toks=[random.choice([1,1,1,4,7,10]) for _ in range(L)]
    if random.random()<0.7: toks=[random.choice([2,5,8,11])]+toks
    a=random.choice([1,1,4,7])
    toks=toks+[a]
    r=random.choice([2,5,8,11,14])
    p=pred(toks,r)
    if p=='USED': used+=1; continue
    res=lit(toks,r,False,60000000)
    cnt+=1
    if res is None or res[0]=='HALT':
        print('NOK',toks,r,res,'pred',p); bad+=1; continue
    st,t2,r2=res
    if (t2,r2)!=p: print('MISMATCH',toks,r,'lit',t2,r2,'pred',p,'step',st); bad+=1
print('done tested',cnt,'used',used,'bad=',bad)
