import idle, sys
from rules import literal
from ztest import predictZ, Z
ds=[]; b=0; total=0; nK=0
for rnd in range(int(sys.argv[1])):
    cfgs=[]; cur=(ds,b)
    for _ in range(1000):
        cfgs.append(cur); p=predictZ(*cur)
        if p[0]!='K': break
        cur=(p[1],p[2])
    res=literal(Z,cfgs,10**10)
    for (d0,b0),r in zip(cfgs,res):
        p=predictZ(d0,b0)
        if not (r[0]=='K' and p[0]=='K' and r[1]==p[1] and r[2]==p[2]): print('MISMATCH',d0,b0,p,r); sys.exit()
        if (b0+sum(d0))%2: print('PHI odd',d0,b0); sys.exit()
        total+=r[3]; nK+=1
    ds,b=cur
    print(f'Z round {rnd}: {nK} K-steps literal-exact, {total} steps, len={len(ds)} b={b} tail {ds[-3:]}',flush=True)
