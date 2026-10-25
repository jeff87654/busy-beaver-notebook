from sim import parse
from itertools import groupby
T=parse(open('discovery_holdouts.txt').read().splitlines()[9]);tape=set();p=0;st=0;n=0
for step in range(5000000):
 if st==7 and p not in tape and p>max(tape,default=-1):
  lo=min(tape);word=''.join('1'if i in tape else'0'for i in range(lo,p));rle=' '.join(f'{k}^{len(list(g))}'for k,g in groupby(word))
  print(step,rle,flush=True);n+=1
  if n>=70:break
 w,d,ns=T[st][int(p in tape)]
 if w:tape.add(p)
 else:tape.discard(p)
 p+=d;st=ns
 if st==-1:print('HALT',step+1);break
