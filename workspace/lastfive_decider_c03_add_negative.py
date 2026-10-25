from pathlib import Path
p=Path('lastfive_decider_c03_independent.py')
s=p.read_text()
s=s.replace('# A boundary above the actual minimum read cannot certify the same trajectory.', '''# Deliberately move the known boundary past a cell this period must read.
negative_boundary=minimum+1
negative_ones={x for x in start if x>=negative_boundary};negative_head=-50;negative_state=5
for rejected_step in range(23636):
 if negative_head<negative_boundary:break
 negative_head,negative_state=step(negative_ones,negative_head,negative_state)
else:raise AssertionError('malformed known boundary was not rejected')''')
s=s.replace("'negative_check':'Any proposed known suffix boundary above minimum read would encounter an unknown cell.'", "'negative_check':{'status':'rejected','proposed_boundary':negative_boundary,'unknown_read_step':rejected_step,'unknown_read_coordinate':negative_head}")
p.write_text(s)
