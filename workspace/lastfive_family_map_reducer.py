"""Exact A/E/H string-rewriting reduction of C16.
Each macro has a direct finite transition proof. No cutoff result is a proof.
"""
from pathlib import Path
from collections import Counter
import json,itertools
from sim import parse
MACHINE=Path('discovery_holdouts.txt').read_text().splitlines()[15]
def macro(t,p,s):
 b=lambda q:int(q in t)
 put=lambda q,v:t.add(q) if v else t.discard(q)
 if s=='A':
  if b(p):
   q=p
   while b(q):q-=1
   return q,'A',p-q,'A1 sweep'
  if not b(p+1):
   put(p,1);return p-1,'A',3,'A00'
  if not b(p+2):
   put(p,1);put(p+1,0);put(p+2,1);return p+3,'A',3,'A010'
  put(p,1);put(p+1,0)
  if not b(p-1):
   put(p-1,1);put(p,0);return p+1,'H',7,'A-left0'
  if not b(p-2):
   put(p-2,1);return p-3,'A',7,'A-left01'
  put(p-2,0);return p-3,'E',7,'A-left11'
 if s=='E':
  if b(p):
   if not b(p-1):
    put(p-1,1);put(p,0);return p+1,'H',3,'E01'
   if not b(p-2):
    put(p-2,1);return p-3,'A',3,'E011'
   put(p-2,0);return p-3,'E',3,'E111'
  put(p,1)
  if not b(p-1):
   put(p-1,1);return p-2,'A',4,'E00'
  if not b(p-2):return p-3,'E',3,'E010'
  # E0,C1,D1(=1RZ): final D1 does not change the existing1.
  return p-1,'Z',3,'E110 halt'
 if s=='H':
  if b(p):
   q=p
   while b(q):put(q,0);q+=1
   return q,'H',q-p,'H1 sweep'
  if not b(p+1):
   put(p,1);put(p+1,1);return p-1,'A',5,'H00'
  q=p+1
  while b(q):put(q,0);q+=1
  put(p,1);return q,'H',q-p+2,'H01run'
 raise AssertionError(s)
def literal(t,p,s,n):
 T=parse(MACHINE);s=ord(s)-65
 for _ in range(n):
  w,d,s=T[s][int(p in t)]
  if w:t.add(p)
  else:t.discard(p)
  p+=d
  if s<0:return t,p,'Z'
 return t,p,chr(65+s)
def check():
 count=0
 for st in 'AEH':
  for mask in range(1<<11):
   original={i-5 for i in range(11) if mask>>i&1};t=original.copy()
   p,s,n,name=macro(t,0,st);tt,pp,ss=literal(original.copy(),0,st,n)
   assert (t,p,s)==(tt,pp,ss),(st,mask,name,n,t,p,s,tt,pp,ss)
   count+=1
 return count
def boundary(ds,cap=100000):
 word='0'.join('1'*r for r in ds);t={i for i,c in enumerate(word)if c=='1'};p=-1;s='A';steps=0;events=Counter()
 for k in range(cap):
  p,s,n,name=macro(t,p,s);steps+=n;events[name]+=1
  if s=='Z':return {'input':ds,'halt':True,'steps':steps,'macros':k+1,'events':events}
  if s=='A' and p==min(t)-1:
   word=''.join(str(int(i in t)) for i in range(p+1,max(t)+1))
   rle=[(c,len(list(g))) for c,g in itertools.groupby(word)]
   runs=[n for c,n in rle if c=='1']
   return {'input':ds,'output':runs,'output_word':word,'output_rle':rle,'all_internal_zero_gaps_one':all(n==1 for c,n in rle if c=='0'),'steps':steps,'macros':k+1,'events':events}
 return {'input':ds,'cutoff_macros':cap,'steps':steps,'events':events}
if __name__=='__main__':
 checks=check();examples=[boundary(ds)for ds in ([3,1],[3,2,1],[4,1],[4,2,1],[3,2,3,1],[4,2,4,1])]
 out={'machine':MACHINE,'exhaustive_finite_macro_crosschecks':checks,'examples':examples}
 Path('lastfive_family_map_reducer.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
