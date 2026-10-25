import sys
from fam import *
for n in range(0,8):
    for a in (0,1):
      for b in range(0,6):
        r=run_next([0]*n,a,b,N=3000000)
        if r[0]=='K':
            ds,aa,bb=r[2]
            print(n,a,b,'->',r[1],'ds=',ds if len(ds)<14 else (len(ds),ds[:3],ds[-3:]),aa,bb, flush=True)
        else:
            print(n,a,b,'->',r[0],r[1], flush=True)
