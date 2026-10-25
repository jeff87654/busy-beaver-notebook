import sys
from fam import *
# R3 with long zero blocks: ds=[y+1]+[0]*k (+ extra digits above), a=0, various b
bad=0
for pre in ([],[3],[0,2]):
  for y1 in (1,2,3):
    for b in range(0,7):
      for k in range(1,16):
        ds=pre+[y1]+[0]*k
        r=run_next(ds,0,b,N=2000000)
        pr=('K',(tuple(pre+[y1-1,b+2]+[0]*(k-1)),0,0))
        if r[0]=='K' and r[2]==pr[1]: continue
        bad+=1
        print('MISMATCH pre',pre,'y+1',y1,'b',b,'k',k,r[:3] if r[0]!='HALT' else ('HALT',r[1],r[2]),flush=True)
print('bad',bad)
