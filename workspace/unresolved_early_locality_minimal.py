"""Independently replayable finite partial-configuration nonhalting certificates.
Only the finite prefix and blank half-line to its left are specified. Reads at
or beyond unknown_start are errors, not an assumed zero. A verified final copy
of the prefix shifted left, with a blank half-line on its left, reestablishes
precisely the same partial configuration for arbitrary right-side contents.
"""
from pathlib import Path
import json
machines=Path('discovery_holdouts.txt').read_text().splitlines()
def check(machine,n,width,steps,shift):
 T=[]
 for row in machine.split('_'):
  T.append([(int(x[0]),1 if x[1]=='R' else -1,-1 if x[2]=='Z' else ord(x[2])-65) for x in (row[:3],row[3:])])
 ones=set(range(n));head=-1;state=0;lo=hi=head
 for t in range(steps):
  if head>=width:raise ValueError(f'unknown suffix read at step {t}, coordinate {head}')
  lo=min(lo,head);hi=max(hi,head)
  w,d,state=T[state][int(head in ones)]
  if w:ones.add(head)
  else:ones.discard(head)
  head+=d
  if state<0:raise ValueError(f'halts at step {t+1}')
 if state!=0 or head!=shift-1:raise ValueError('final state or head mismatches recurrence')
 if {p for p in ones if p<shift+width}!=set(range(shift,shift+n)):
  raise ValueError('final blank half-line or finite prefix mismatches recurrence')
 return {'read_bounds':[lo,hi],'final_head':head,'final_state':'A','known_final_ones':sorted(ones),
         'new_unknown_suffix_start':shift+width}

results=[]
for c,n,width,steps,shift,seed in [(5,3,8,30494,-324,30517),(6,2,9,12611,-205,12631)]:
 machine=machines[c-1];result=check(machine,n,width,steps,shift)
 negative=[]
 for label,mm,ww,tt in [('unknown boundary one cell too close',machine,width-1,steps),
                       ('incorrect cycle time',machine,width,steps-1),
                       ('first transition changed to halt','1RZ'+machine[3:],width,steps)]:
  try:check(mm,n,ww,tt,shift)
  except ValueError as e:negative.append({'mutation':label,'status':'rejected','reason':str(e)})
  else:raise AssertionError(('malformed certificate accepted',c,label))
 results.append({'candidate':f'C{c:02}','machine':machine,'initial_state':'A','initial_head':-1,
                 'left_background':0,'known_prefix':'1'*n+'0'*(width-n),'unknown_suffix_start':width,
                 'cycle_steps':steps,'displacement':shift,'blank_seed_steps':seed,
                 'check':result,'negative_checks':negative,'status':'verified_partial_configuration_recurrence'})
Path('unresolved_early_locality_minimal.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
