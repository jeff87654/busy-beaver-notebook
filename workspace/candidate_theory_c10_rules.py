import json,re
from sim import parse
from itertools import groupby
from pathlib import Path
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[9])
def decode(w):
 if set(w)=={'1'}:return ['D',len(w)]
 if w.endswith('01')and set(w[:-2])=={'1'}:return['E',len(w)-2]
 m=re.fullmatch(r'1111((?:01)*)0(1+)01',w)
 if m:return['C',len(m[1])//2,len(m[2])]
 return['other',w[:200]]
def run(w,limit=2000000):
 t={i for i,c in enumerate(w)if c=='1'};p=len(w);st=7
 for z in range(limit):
  if z and st==7 and p>max(t,default=-1):
   word=''.join('1'if i in t else'0'for i in range(min(t),p));return z,decode(word)
  wr,d,ss=T[st][int(p in t)]
  if wr:t.add(p)
  else:t.discard(p)
  p+=d;st=ss
  if st==-1:return z+1,['halt',len(t)]
 return limit,['cutoff']
results=[]
for b in [1,3,5,7,9,11,13,25,37]:
 for a in [0,1,2,3,4,5,6,10,20,50]:
  w='1111'+'01'*a+'0'+'1'*b+'01';r=run(w);row=['C',a,b,*r];results.append(row);print(row,flush=True)
for n in range(4,45):
 for typ in ['D','E']:
  w='1'*n+('01'if typ=='E'else'');r=run(w);row=[typ,n,*r];results.append(row);print(row,flush=True)
Path('candidate_theory_c10_rules.json').write_text(json.dumps(results,indent=2))
