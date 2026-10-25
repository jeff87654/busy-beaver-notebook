import json
from pathlib import Path
from sim import parse
machines=Path('discovery_holdouts.txt').read_text().splitlines()
results=[]
for index in (5,6):
 T=parse(machines[index-1])
 for gap in (1,3):
  for n in range(1,49):
   ones=set(range(n));ones.add(n+gap);head=-1;state=0
   for steps in range(1,100000):
    w,d,state=T[state][int(head in ones)]
    if w:ones.add(head)
    else:ones.discard(head)
    head+=d
    if state<0:out=['halt',len(ones)];break
    if state==0 and head==min(ones)-1:
     lo,hi=min(ones),max(ones)
     word=''.join('1'if p in ones else'0'for p in range(lo,hi+1))
     a=len(word)-len(word.lstrip('1'));tail=word[a:];b=len(tail)-len(tail.lstrip('0'))
     if tail[b:]=='1':out=['return',a,b];break
   else:out=['cutoff']
   row={'candidate':f'C{index:02}','n':n,'gap':gap,'steps':steps,'out':out};results.append(row)
 Path('unresolved_early_maps.json').write_text(json.dumps(results,indent=2))
for row in results:
 if row['n']<=16:print(row)
trace=json.loads(Path('unresolved_early_trace.json').read_text())
for row in trace:
 print(row['candidate'],[(s['steps'],s['rle'])for s in row['snapshots']if s['state']=='A'and s['headRelative']==-1 and len(s['rle'])==3])
