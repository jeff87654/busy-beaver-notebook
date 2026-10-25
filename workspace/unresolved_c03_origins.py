from pathlib import Path
from collections import Counter
import json
from sim import parse
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[2]); tape=set();p=st=0
lastC=None;lastH=None;origins=Counter();bad=[];hpaths=Counter();hpath=None
for step in range(2_000_000):
 r=int(p in tape)
 if st==2: lastC=step
 if st==7 and r: lastH=step;hpath=[]
 elif hpath is not None:
  hpath.append(chr(65+st)+str(r))
  if st in (0,1,2) or (st==5 and r):
   hpaths[' '.join(hpath)]+=1;hpath=None
 if st==5 and r:
  ori='C' if lastH is None or lastC>lastH else 'H';origins[ori]+=1
  if ori=='H' and len(bad)<20: bad.append([step,p,lastC,lastH, ''.join(str(int(p+j in tape)) for j in range(-8,16))])
 w,d,st=T[st][r]
 if w:tape.add(p)
 else:tape.discard(p)
 p+=d
 if st<0:break
out={'origins':origins,'H_origin_examples':bad,'H_paths':hpaths}
Path('unresolved_c03_origins.json').write_text(json.dumps(out,indent=2))
print(out)
