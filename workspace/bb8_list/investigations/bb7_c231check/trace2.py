import idle,sys
from rsim import *
from rules import isk
M = M1 if sys.argv[1]=='1' else M2
r=RSim(M,[],0,[],0)
while r.steps<int(sys.argv[2]):
    res=r.run_until(isk,int(sys.argv[2]))
    if res!='HIT': print(res,r.steps,r.ones()); break
    k=parse_k(r)
    if k: print(r.steps,k[0],len(k[1]),k[1][:4])
