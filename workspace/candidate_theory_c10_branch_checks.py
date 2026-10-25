import json
from pathlib import Path
exec(Path('candidate_theory_c10_rules.py').read_text().split('results=[]')[0])
checks=0
for b in range(1,102,2):
 d=(b+9)//2
 for a in sorted({0,1,d-2,d-1,d,d+1,2*d}):
  actual=run('1111'+'01'*a+'0'+'1'*b+'01')
  if a==0:expected=(b+14,['halt',(b+15)//2])
  elif a>=d:expected=((3*b*b+36*b+121)//2,['C',a-d,2*b+11])
  else:expected=(3*a*a-(3*b+42)*a+(9*b*b+156*b+683)//4,['E',3*b-2*a+21])
  assert actual==expected,(a,b,actual,expected)
  checks+=1
Path('candidate_theory_c10_branch_checks.json').write_text(json.dumps({'finite_checks':checks,'all_passed':True,'scope':'Empirical checks of C branches, not a universal proof'},indent=2))
print('Passed',checks,flush=True)
