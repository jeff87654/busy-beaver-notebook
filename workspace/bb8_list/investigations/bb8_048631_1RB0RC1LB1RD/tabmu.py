import random,sys
from randlist import run
from phi import phi
random.seed(3)
a=int(sys.argv[1]); M=int(sys.argv[2])
rows=[]
for m in range(0,M+1):
    line=[]
    for u in range(0,m+1):
        res=set()
        for rep in range(2):
            pos=random.sample(range(m),u)
            P=tuple(1 if i in pos else 2 for i in range(m))
            ts=P+(40,)
            r=run(a,ts,500000000)
            assert r[0]=='std'
            res.add((r[1][0],r[1][1][:-1] if r[1][1] and r[1][1][-1]==38 else r[1][1]))
        ok = (len(res)==1)
        (a2,l)=sorted(res)[0]
        exp=phi(a,P+(40,))
        flag='' if (a2,l+(38,))==exp or (a2,l)==exp else '*'
        line.append((u,a2,l,'indep' if ok else 'DEP',flag))
    rows.append((m,line))
    print(m,[(x[0],x[1],x[2],x[4]) for x in line if x[4]=='*' or not x[3]=='indep'][:6], 'bad' if any(x[4]=='*' for x in line) else 'ok', flush=True)
