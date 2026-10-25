"""Search exact one-sided recurring configurations, requiring an uncrossed boundary."""
from pathlib import Path
import json,time
from sim import parse
out=[]
for idx in (13,15):
 machine=Path('discovery_holdouts.txt').read_text().splitlines()[idx];T=parse(machine)
 p=s=0;tape=0;offset=4096;contexts=(0,4,8,16,32,64,128,256,512,1024);seenR={k:{}for k in contexts};seenL={k:{}for k in contexts};last={};events=0;matches=[];start=time.monotonic();limit=10_000_000
 for step in range(limit):
  assert p+offset>=0
  r=(tape>>(p+offset))&1
  if s==4 and r==0:
   events+=1
   for k in contexts:
    if p-k+offset<0:continue
    key=tape>>(p-k+offset);old=seenR[k].get(key)
    if old:
     oldstep,oldp=old
     if p>=oldp and last.get(oldp-k-1,-1)<oldstep:matches.append({'direction':'right','steps':[oldstep,step],'heads':[oldp,p],'context':k,'state':s})
    seenR[k][key]=(step,p)
    boundary=p+k+offset;prefix=tape&((1<<(boundary+1))-1)
    if prefix:
     first=(prefix&-prefix).bit_length()-1
     key=(prefix>>first,boundary-first)
    else:key=(0,0)
    old=seenL[k].get(key)
    if old:
     oldstep,oldp=old
     if p<=oldp and last.get(oldp+k+1,-1)<oldstep:matches.append({'direction':'left','steps':[oldstep,step],'heads':[oldp,p],'context':k,'state':s})
    seenL[k][key]=(step,p)
   if matches:break
  last[p]=step
  w,d,s=T[s][r]
  if w:tape|=1<<(p+offset)
  else:tape&=~(1<<(p+offset))
  p+=d
  if s<0:break
  if time.monotonic()-start>100:break
 result={'id':f'C{idx+1:02}','machine':machine,'steps_simulated':step+1,'events':events,'status':'halt'if s<0 else'candidate_recurrence'if matches else'cutoff','matches':matches,'elapsed_seconds':time.monotonic()-start,'ones':tape.bit_count()}
 out.append(result);Path('lastfive_cycle_search.json').write_text(json.dumps(out,indent=2));print(json.dumps(result),flush=True)
