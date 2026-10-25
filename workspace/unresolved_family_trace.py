"""Exact finite H0 checkpoints for C13-C16; no extrapolated classifications."""
import json,time
from pathlib import Path
from itertools import groupby
from sim import parse
LIMIT=2_000_000
rows=json.loads(Path('candidate_manifest.json').read_text())[12:16]
out={'limit':LIMIT,'results':[]}
for row in rows:
 T=parse(row['machine']);origin=LIMIT+4;tape=bytearray(2*LIMIT+10);p=origin;s=0;lo=hi=p;ones=0;ev=0;snap=[];start=time.monotonic()
 for n in range(LIMIT):
  b=tape[p]
  if s==7 and b==0:
   ev+=1
   if ev<=24 or ev&(ev-1)==0:
    inds=[i for i in range(lo,hi+1) if tape[i]]
    aa=min(inds+[p]);bb=max(inds+[p]);word=tape[aa:bb+1]
    runs=[(int(k),len(list(g))) for k,g in groupby(word)]
    snap.append({'event':ev,'step':n,'head':p-aa,'ones':ones,'word':''.join(map(str,word)) if len(word)<1000 else None,'run_count':len(runs),'runs':runs if len(runs)<160 else runs[:80]+runs[-80:]})
  w,d,ns=T[s][b];tape[p]=w;ones+=w-b;p+=d;s=ns;lo=min(lo,p);hi=max(hi,p)
  if s==-1:raise AssertionError((row['id'],'HALT',n+1,ones))
 result=dict(row,H0_count=ev,checkpoints=snap,elapsed_seconds=time.monotonic()-start)
 out['results'].append(result)
 Path('unresolved_family_trace.json').write_text(json.dumps(out,indent=2))
 print(row['id'],'H0',ev,'last',snap[-1]['step'],snap[-1]['ones'],'runs',snap[-1]['run_count'],flush=True)
