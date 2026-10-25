"""Independent literal replay of C03's translated suffix-cycle certificate.
No simulator import or macro transitions; each loop executes one TM step.
"""
from pathlib import Path
import json, hashlib
machine=Path('discovery_holdouts.txt').read_text().splitlines()[2]
expected='1RB1LA_0LA0RC_1RA1LD_0LE0LF_0RA0LD_0LC0RG_1RH1RZ_0RG0RE'
assert machine==expected
rules={}
for state,row in zip('ABCDEFGH',machine.split('_')):
 for read,transition in enumerate((row[:3],row[3:])):
  rules[state,read]=(int(transition[0]),1 if transition[1]=='R' else -1,transition[2])
start=83806;period=23636;drift=32;boundary=-54
ones=set();head=0;state='A';snapshots={};ranges=[];mn=10**9;mx=-10**9
for step in range(start+3*period+1):
 if step>=start:
  index=(step-start)//period
  if (step-start)%period==0:
   if index:ranges.append({'period_index':index-1,'minimum_read_head':mn,'maximum_read_head':mx})
   snapshots[index]={'step':step,'state':state,'head':head,'all_ones':sorted(ones),'suffix_ones_relative_to_boundary':sorted(x-(boundary+index*drift) for x in ones if x>=boundary+index*drift)}
   mn=10**9;mx=-10**9
  mn=min(mn,head);mx=max(mx,head)
 if step==start+3*period:break
 read=int(head in ones);write,direction,nextstate=rules[state,read]
 if write:ones.add(head)
 else:ones.discard(head)
 head+=direction;state=nextstate
 assert state!='Z',('unexpected halt',step+1)
first=snapshots[0]
for i,snap in snapshots.items():
 assert snap['state']==first['state']=='F'
 assert snap['head']==first['head']+i*drift
 assert snap['suffix_ones_relative_to_boundary']==first['suffix_ones_relative_to_boundary']
for i,ran in enumerate(ranges):
 assert ran['minimum_read_head']>=boundary+i*drift
 assert ran['minimum_read_head']==ranges[0]['minimum_read_head']+i*drift
 assert ran['maximum_read_head']==ranges[0]['maximum_read_head']+i*drift
proof={'candidate_id':'C03','machine':machine,'classification':'nonhalting','method':'translated suffix cycle','initial_steps':start,'period_steps':period,'head_displacement':drift,'initial_left_boundary':boundary,'state':first['state'],'initial_head':first['head'],'suffix_ones_relative_to_boundary':first['suffix_ones_relative_to_boundary'],'period_read_head_min':ranges[0]['minimum_read_head'],'period_read_head_max':ranges[0]['maximum_read_head'],'extra_period_replays':2,'snapshots':snapshots,'ranges':ranges,'argument':'The first period never reads left of the boundary. At its end the state and entire suffix at or right of the boundary recur translated by +32. Determinism repeats the same finite transition sequence translated by +32 in every subsequent period, and its read positions remain within that suffix. Hence the machine runs forever.'}
proof['verifier_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
Path('unresolved_c03_cycle_certificate.json').write_text(json.dumps(proof,indent=2))
print(json.dumps({k:v for k,v in proof.items() if k not in ['snapshots','suffix_ones_relative_to_boundary','argument']},indent=2))
