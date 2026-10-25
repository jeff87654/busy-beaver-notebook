from sim import parse
from itertools import groupby
T=parse(open('discovery_holdouts.txt').read().splitlines()[6]);tape=set();p=0;st=0;count=0
for step in range(200000):
 if st in (6,7) and (step<500 or (st==7 and count<50)):
  lo=min(tape|{p});hi=max(tape|{p});word=''.join('1'if i in tape else'0'for i in range(lo,hi+1));rle=' '.join(f'{k}^{len(list(g))}'for k,g in groupby(word))
  print(step,chr(65+st),p-lo,'read',int(p in tape),'range',lo,hi,rle,flush=True);count+=st==7
 w,d,ns=T[st][int(p in tape)]
 if w:tape.add(p)
 else:tape.discard(p)
 p+=d;st=ns
 if st==-1:print('halt',step+1);break
