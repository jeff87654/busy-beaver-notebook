from sim import parse
from itertools import groupby
TMS=open('discovery_holdouts.txt').read().splitlines()
for idx in [9,10]:
 T=parse(TMS[idx-1]);tape=set();p=0;st=0;n=0
 for step in range(1000000):
  if st in (6,7) and (step<200 or (st==7 and n<35)):
   lo=min(tape|{p});hi=max(tape|{p});word=''.join('1'if i in tape else'0'for i in range(lo,hi+1));rle=' '.join(f'{k}^{len(list(g))}'for k,g in groupby(word))
   print(idx,step,chr(65+st),p-lo,'read',int(p in tape),rle,flush=True);n+=st==7
  w,d,ns=T[st][int(p in tape)]
  if w:tape.add(p)
  else:tape.discard(p)
  p+=d;st=ns
  if st==-1:print('HALT',idx,step+1,len(tape));break
