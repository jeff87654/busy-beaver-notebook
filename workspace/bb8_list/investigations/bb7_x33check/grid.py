import idle, sys
from rules import *
m = X if sys.argv[1]=='X' else I
for pre in ([1],[2],[3],[5,1],[1,7],[2,2]):
    cfgs=[]; keys=[]
    for k in range(1,14):
        for b in range(1, 2*k+3):
            cfgs.append((pre+[0]*k,b)); keys.append((k,b))
    res=literal(m,cfgs,10**7)
    print('prefix',pre)
    for k in range(1,14):
        row=[]
        for (kk,b),r,(ds,_) in zip(keys,res,cfgs):
            if kk!=k: continue
            pr=predict(ds,b)
            ok = (pr[0]==r[0]) and ((pr[0]=='HALT' and pr[1]==r[1]) or (pr[0]=='K' and pr[1]==r[1] and pr[2]==r[2]))
            row.append('.' if ok else ('H' if r[0]=='HALT' else ('T' if r[0]=='TIMEOUT' else 'x')))
        print(f' k={k:2d}', ''.join(row), ' (b=1..)')
