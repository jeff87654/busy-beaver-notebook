from sim import parse
from itertools import groupby
TMS=open('discovery_holdouts.txt').read().splitlines()
def run(idx,n,k=2,limit=1000000):
 T=parse(TMS[idx-1]);tape=set(range(-n,0))|set(range(1,k+1));p=0;st=7
 for step in range(limit):
  if step and st==7:
   lo=min(tape|{p});hi=max(tape|{p});rle=[(z,len(list(g)))for z,g in groupby(''.join('1'if i in tape else'0'for i in range(lo,hi+1)))];return step, p-lo,int(p in tape),rle
  w,d,ns=T[st][int(p in tape)]
  if w:tape.add(p)
  else:tape.discard(p)
  p+=d;st=ns
  if st==-1:return 'halt',step+1
 return 'cutoff',limit
for idx in [7,8]:
 for n in range(1,34): print(idx,n,run(idx,n),flush=True)
