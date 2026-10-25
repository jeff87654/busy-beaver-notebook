import idle, sys, random
from rules import *
# chain literal K->K runs along the rule-level trajectory starting at blank (E with B=0)
ds=[]; b=0; total=0; nK=0; batch=int(sys.argv[1]); rounds=int(sys.argv[2]); maxb=int(sys.argv[3])
for rnd in range(rounds):
    cfgs=[]; cur=(ds,b)
    for _ in range(batch):
        cfgs.append(cur)
        p=predict(*cur)
        if p[0]!='K': break
        cur=(p[1],p[2])
    res=literal(X,cfgs,10**10)
    for (d0,b0),r in zip(cfgs,res):
        p=predict(d0,b0)
        if not (r[0]=='K' and p[0]=='K' and r[1]==p[1] and r[2]==p[2]):
            print('MISMATCH',d0,b0,p,r); sys.exit()
        if (b0+sum(d0))%2: print('PHI odd!',d0,b0); sys.exit()
        total+=r[3]; nK+=1
    ds,b=cur
    print(f'round {rnd}: {nK} K-steps verified literal, {total} steps, now len={len(ds)} b={b} last digits {ds[-4:]}', flush=True)
    if b>maxb: break
