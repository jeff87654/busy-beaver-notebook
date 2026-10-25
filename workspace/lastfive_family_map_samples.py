from pathlib import Path
from sim import parse
import itertools,json
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[15])
def run(ds,cap=100000):
 word='0'.join('1'*r for r in ds);t={i for i,c in enumerate(word)if c=='1'};p=-1;s=0
 for k in range(cap):
  w,d,s=T[s][int(p in t)]
  if w:t.add(p)
  else:t.discard(p)
  p+=d
  if s<0:return {'input':ds,'halt':k+1}
  if s==0 and p==min(t)-1:
   word=''.join(str(int(i in t))for i in range(p+1,max(t)+1));runs=[len(list(g)) for c,g in itertools.groupby(word)if c=='1'];zeros=[len(list(g))for c,g in itertools.groupby(word)if c=='0'];return {'input':ds,'output':runs,'zero_runs':zeros,'steps':k+1}
 return {'input':ds,'cutoff':cap}
if __name__=='__main__':
 out=[]
 for n in (2,3,4):
  for k in range(3):
   for tail in itertools.product((2,3),repeat=k):out.append(run([n,*tail,1]))
 for n in (2,3):
  for k in range(4):out.append(run([n]+[2]*k+[4,1]))
 Path('lastfive_family_map_samples.json').write_text(json.dumps(out,indent=2))
 for x in out:print(x)
