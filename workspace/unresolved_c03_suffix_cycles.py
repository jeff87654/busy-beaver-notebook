from pathlib import Path
from collections import Counter
import json,time
from sim import parse
machine=Path('discovery_holdouts.txt').read_text().splitlines()[2];T=parse(machine)
p=s=0;tape=0;offset=4096;seen={k:{} for k in [0,4,8,16,32,64,128,256,512,1024]};last={};matches=[];count=0;start=time.monotonic()
for step in range(2_000_000):
 r=(tape>>(p+offset))&1
 if s==5 and r:
  count+=1
  for k,dct in seen.items():
   tail=tape>>(p-k+offset);key=tail
   if key in dct:
    oldstep,oldp=dct[key]
    if p>=oldp and last.get(oldp-k-1,-1)<oldstep:
     matches.append({'steps':[oldstep,step],'heads':[oldp,p],'left_context':k,'suffix_bits_little_endian':bin(tail)[2:][::-1], 'last_crossing':last.get(oldp-k-1,-1)})
   dct[key]=(step,p)
  if matches:break
 last[p]=step
 w,d,s=T[s][r]
 if w:tape|=1<<(p+offset)
 else:tape&=~(1<<(p+offset))
 p+=d
 if s<0:break
out={'machine':machine,'steps':step+1,'events':count,'elapsed':time.monotonic()-start,'matches':matches,'unique_suffixes':{k:len(v) for k,v in seen.items()}}
Path('unresolved_c03_suffix_cycles.json').write_text(json.dumps(out,indent=2));print(out)
