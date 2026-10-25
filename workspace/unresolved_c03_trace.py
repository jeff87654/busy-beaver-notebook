from pathlib import Path
from itertools import groupby
import json
from sim import parse
machine=Path('discovery_holdouts.txt').read_text().splitlines()[2];T=parse(machine)
tape=set();p=st=0;events=[];count=0
for step in range(2000000):
 r=int(p in tape)
 if st==5 and r==1:
  count+=1
  if count<=100 or count&(count-1)==0:
   lo=min(tape|{p});hi=max(tape|{p});word=''.join('1' if x in tape else '0' for x in range(lo,hi+1))
   rec={'event':count,'step':step,'head':p,'leftmost':lo,'rightmost':hi,'ones':len(tape),'relative_ones':sorted(x-p for x in tape),'runs':[[ch,len(list(g))] for ch,g in groupby(word)]}
   events.append(rec)
 w,d,ns=T[st][r]
 if w:tape.add(p)
 else:tape.discard(p)
 p+=d;st=ns
 if st<0:break
payload={'machine':machine,'steps':step+1,'halt':st<0,'total_F1_events':count,'events':events}
Path('unresolved_c03_trace.json').write_text(json.dumps(payload,indent=2))
for e in events[:25]+events[-6:]:print(e)
print('summary',step+1,st,count,len(tape))
