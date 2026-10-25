import json
from pathlib import Path
from sim import parse
rows=json.loads(Path('candidate_manifest.json').read_text())
out=[]
for row in rows[10:]:
 t=parse(row['machine']); tape=set();p=st=0;lo=hi=0;events=[];lastn={}
 for step in range(100000):
  cur=int(p in tape)
  if st in (3,4,5,6,7) and not cur and step>0 and step%1024==0 and step>lastn.get(st,-100)*1.6+10:
   if len(tape)<2000:
    a=min(tape,default=p);b=max(tape,default=p)
    if p<=a or p>=b or st==7:
     s=''.join('1' if q in tape else '0' for q in range(a,b+1))
     runs=[]
     for ch in s:
      if runs and runs[-1][0]==ch:runs[-1][1]+=1
      else:runs.append([ch,1])
     if len(runs)<30:
      events.append({'step':step,'state':chr(st+65),'head':p-a,'ones':len(tape),'runs':runs})
      lastn[st]=step
  w,d,ns=t[st][cur]
  if w:tape.add(p)
  else:tape.discard(p)
  p+=d;st=ns
  if st<0:break
 out.append({'id':row['id'],'events':events,'halt':st<0,'steps':step+1})
Path('candidate_root_traces.json').write_text(json.dumps(out,indent=2))
for r in out:
 print(r['id'],r['events'][-6:])
