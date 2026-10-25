"""Literal bounded profiles of resolved machines; these observations are not proofs."""
import json,time
from pathlib import Path
from itertools import groupby
from sim import parse
IDS={'C01','C02','C04','C07','C08','C10','C11','C12'}
LIMIT=1_000_000
rows=[r for r in json.loads(Path('candidate_manifest.json').read_text()) if r['id'] in IDS]
out={'purpose':'Finite behavior profiles only; nonhalting classifications come from separate proofs.','step_limit':LIMIT,'results':[]}
for row in rows:
 start=time.monotonic();T=parse(row['machine']);tape=bytearray(2*LIMIT+16);origin=LIMIT+8;p=origin;s=0;ones=0;lo=hi=p
 halt=[(i,b) for i,rr in enumerate(T) for b,e in enumerate(rr) if e[2]==-1]
 hist=[[0,0] for _ in T];snaps=[];entries=[]
 def snapshot(n):
  word=tape[lo:hi+1];runs=[(int(k),len(list(g))) for k,g in groupby(word)]
  return {'step':n,'state':chr(65+s),'head':p-origin,'ones':ones,'visited_left':lo-origin,'visited_right':hi-origin,'visited_span':hi-lo+1,'run_count':len(runs),'left_runs':runs[:18],'right_runs':runs[-18:] if len(runs)>18 else [],'read':int(tape[p])}
 for n in range(LIMIT):
  b=tape[p]
  if len(entries)<12 and any(s==hs for hs,hb in halt):entries.append(snapshot(n))
  hist[s][b]+=1;w,d,ns=T[s][b];tape[p]=w;ones+=w-b;p+=d;s=ns
  if p<lo:lo=p
  if p>hi:hi=p
  if s==-1:raise AssertionError(('Unexpected halt in resolved candidate',row['id'],n+1))
  if n+1 in (100,1000,10000,100000,LIMIT):snaps.append(snapshot(n+1))
 result=dict(row,halt_preconditions=[chr(65+s)+str(b) for s,b in halt],snapshots=snaps,first_halt_state_visits=entries,state_symbol_counts=hist,elapsed_seconds=time.monotonic()-start)
 out['results'].append(result)
 print(row['id'],snaps[-1]['ones'],snaps[-1]['visited_span'],snaps[-1]['run_count'],round(result['elapsed_seconds'],2),flush=True)
Path('resolved_profiles.json').write_text(json.dumps(out,indent=2))
