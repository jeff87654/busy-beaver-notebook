import json,re,itertools
from pathlib import Path
from sim import parse
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[8])
def one(n,tail,limit=100000):
 word='10'*n+'11'+tail;end=len(word)+1;t={i+1 for i,c in enumerate(word)if c=='1'};p=0;s=5;dt=0
 while dt<limit:
  if p>=end:return ['unknown',dt]
  if dt and s==5 and p not in t and min(t,default=end)==p+1:
   w=''.join('1'if i in t else'0'for i in range(p+1,end));m=re.match(r'((?:10)*)11(.*)',w)
   if m:return ['K',dt,len(m[1])//2,m[2],p]
   return ['other',dt,w,p]
  r=int(p in t);wr,d,ss=T[s][r]
  if wr:t.add(p)
  else:t.discard(p)
  p+=d;s=ss;dt+=1
  if s==-1:return['halt',dt]
 return['cutoff',dt]
records=[]
for n in [1,2,4,6,8]:
 for w in map(''.join,itertools.product('01',repeat=8)):
  r=one(n,w);records.append([n,w,r])
Path('unresolved_c09_local_rules.json').write_text(json.dumps(records,indent=2))
for n in [1,2,4]:
 seen={}
 for nn,w,r in records:
  if nn!=n:continue
  key=tuple(r[:1]+r[2:3])
  if key not in seen: seen[key]=[]
  if len(seen[key])<4:seen[key].append((w,r))
 print(n,seen,flush=True)
