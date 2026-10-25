"""Finite locality certificates proving arbitrary-suffix expansion, not mere sampling.
A proof checker must establish that every transition reads a known cell, then
check exactly the asserted output on that known half-line. Cells beyond the
boundary are uninterpreted and may have arbitrary contents.
"""
from pathlib import Path
import json
M=Path('discovery_holdouts.txt').read_text().splitlines()
out=[]
for c,n,gap,tail,period,seed in [(5,3,327,323,30494,30517),(6,2,210,204,12611,12631)]:
 machine=M[c-1]
 T=[]
 for row in machine.split('_'):
  T.append([(int(x[0]),1 if x[1]=='R' else -1,-1 if x[2]=='Z' else ord(x[2])-65)for x in(row[:3],row[3:])])
 prefix='1'*n+'0'*gap+'1'; unknown=len(prefix)
 ones={i for i,s in enumerate(prefix)if s=='1'}; head=-1;state=0
 minimum=maximum=head;write_min=write_max=head
 reads_at_marker=0;write_marker=False
 for step in range(period):
  assert head<unknown,('read unknown suffix',c,step,head)
  minimum=min(minimum,head);maximum=max(maximum,head)
  reads_at_marker+=head==unknown-1
  w,d,state=T[state][int(head in ones)]
  write_min=min(write_min,head);write_max=max(write_max,head)
  write_marker|=head==unknown-1
  if w:ones.add(head)
  else:ones.discard(head)
  head+=d
  assert state>=0,('halt',c,step)
 shift=-(tail+1)
 assert state==0 and head==-1+shift
 expected=prefix+('0'*tail+'1')
 expected_ones={i+shift for i,s in enumerate(expected)if s=='1'}
 assert ones==expected_ones,(c,sorted(ones),sorted(expected_ones))
 assert shift+len(expected)==unknown
 out.append({'candidate':f'C{c:02}','machine':machine,'blank_seed_steps':seed,'cycle_steps':period,
  'initial_head':-1,'initial_state':'A','known_domain':{'left':'negative_infinity','right_inclusive':unknown-1},
  'initial_prefix':prefix,'initial_ones':[i for i,x in enumerate(prefix)if x=='1'],
  'unknown_suffix_start':unknown,'read_bounds':[minimum,maximum],'write_bounds':[write_min,write_max],
  'terminal_marker_index':unknown-1,'terminal_marker_reads':reads_at_marker,'terminal_marker_written':write_marker,
  'final_head':head,'final_state':'A','head_displacement':shift,'final_ones':sorted(ones),
  'final_prefix':expected,'final_prefix_start':shift,'final_prefix_end_exclusive':unknown,
  'claims_checked':['Every read and write stays in the known half-line.',
   'The known half-line equals the claimed expanded prefix with zero background.',
   'The arbitrary suffix is neither read nor written, and its starting coordinate is unchanged.',
   'Final state/head and tape are exactly the next expansion-family member.'],
  'status':'verified_finite_locality_certificate'})
Path('unresolved_early_locality_python.json').write_text(json.dumps(out,indent=2))
for x in out:
 print({k:v for k,v in x.items()if k not in('initial_prefix','final_prefix','claims_checked','machine')})

