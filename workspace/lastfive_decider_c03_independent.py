from pathlib import Path
import json
machine=Path('discovery_holdouts.txt').read_text().splitlines()[2]
T=[[(int(x[0]),1 if x[1]=='R' else -1,-1 if x[2]=='Z' else ord(x[2])-65) for x in(row[:3],row[3:])] for row in machine.split('_')]
def step(ones,head,state):
 w,d,state=T[state][int(head in ones)]
 if w:ones.add(head)
 else:ones.discard(head)
 return head+d,state
ones=set();head=0;state=0
for i in range(83806):
 head,state=step(ones,head,state)
 assert state>=0
assert state==5 and head==-50
boundary=head-4;start={x for x in ones if x>=boundary}
known=set(start);h=head;s=state;minimum=maximum=h
for i in range(23636):
 assert h>=boundary,('unknown read',i,h)
 minimum=min(minimum,h);maximum=max(maximum,h)
 h,s=step(known,h,s)
 assert s>=0
assert s==state and h==head+32
final={x for x in known if x>=boundary+32}
assert final=={x+32 for x in start}
for i in range(23636):
 head,state=step(ones,head,state)
 assert state>=0
assert h==head and s==state and final=={x for x in ones if x>=boundary+32}
# Deliberately move the known boundary past a cell this period must read.
negative_boundary=minimum+1
negative_ones={x for x in start if x>=negative_boundary};negative_head=-50;negative_state=5
for rejected_step in range(23636):
 if negative_head<negative_boundary:break
 negative_head,negative_state=step(negative_ones,negative_head,negative_state)
else:raise AssertionError('malformed known boundary was not rejected')
result={'candidate':'C03','machine':machine,'status':'independently_verified_partial_configuration_recurrence',
 'seed_steps':83806,'cycle_steps':23636,'state':'F','initial_head':-50,'final_head':h,'displacement':32,
 'known_initial_region':{'left_inclusive':boundary,'right':'positive_infinity'},'read_write_bounds':[minimum,maximum],
 'known_initial_ones':sorted(start),'final_comparison_region':{'left_inclusive':boundary+32,'right':'positive_infinity'},
 'known_final_ones':sorted(final),'initial_unknown_cells_never_read':True,
 'final_suffix_exact_translated_copy':True,'full_blank_simulation_matches':True,
 'negative_check':{'status':'rejected','proposed_boundary':negative_boundary,'unknown_read_step':rejected_step,'unknown_read_coordinate':negative_head}}
Path('lastfive_decider_c03_independent.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

