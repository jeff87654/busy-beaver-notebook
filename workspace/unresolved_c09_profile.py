from sim import parse
from pathlib import Path
import json
from itertools import groupby
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[8]);t=set();p=0;s=0;lo=hi=0;out=[]
for z in range(2000001):
 if z and s in [0,5] and p not in t:
  leftedge=(s==5 and p+1 in t and not any(i<p for i in t))
  rightedge=(s==0 and p-1 in t and not any(i>p for i in t))
  if leftedge or rightedge:
   w=''.join('1'if i in t else'0'for i in range(min(t),max(t)+1));runs=[len(list(g))for _,g in groupby(w)]
   row={'steps':z,'state':chr(65+s),'head':p,'ones':len(t),'runs':runs,'side':'left'if leftedge else'right'};out.append(row)
   if len(out)<=35:print(row,flush=True)
 w,d,ns=T[s][int(p in t)]
 if w:t.add(p)
 else:t.discard(p)
 p+=d;s=ns
 if s==-1:print('HALT',z+1,len(t));break
Path('unresolved_c09_profile.json').write_text(json.dumps({'machine':Path('discovery_holdouts.txt').read_text().splitlines()[8],'steps':z+1,'halted':s==-1,'snapshots':out},indent=2))
