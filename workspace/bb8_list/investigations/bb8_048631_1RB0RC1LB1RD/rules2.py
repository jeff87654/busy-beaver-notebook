import itertools,sys
from randlist import run
T0=30
def succ(a,ts):
    r=run(a,ts,20000000)
    assert r[0]=='std',(a,ts,r)
    return r[1]
res={}
for a in (2,3):
    print('== a =',a)
    for m in range(0,8):
        for P in itertools.product((1,2),repeat=m):
            ts=P+(T0,)
            a2,r=succ(a,ts)
            # r should end with (T0-2,)
            assert r[-1]==T0-2,(a,P,r)
            Q=r[:-1]
            res[(a,P)]=(a2,Q)
            print(a,P,'->',(a2,Q))
import json
json.dump({str(k):v for k,v in res.items()},open('rules2.json','w'))
