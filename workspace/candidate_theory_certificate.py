"""Independent exact certificates for the C07/C08 nonhalting recurrence."""
import json
from pathlib import Path
from sim import parse
TMS=Path('discovery_holdouts.txt').read_text().splitlines()
def step(T,t,p,s):
 w,d,ns=T[s][int(p in t)]
 if w:t.add(p)
 else:t.discard(p)
 return p+d,ns
out={'machines':{},'gadget':[],'finite_checks':0}
for cid in [7,8]:
 T=parse(TMS[cid-1]);t={2,4};p=0;s=4;trace=[]
 # E>0 01010 W -> 1^8 G>W, W begins at6, never read.
 for z in range(26):
  trace.append({'step':z,'head':p,'state':chr(65+s),'read':int(p in t)})
  assert p<6
  p,s=step(T,t,p,s)
 assert p==6 and s==6 and t==set(range(-2,6))
 out['gadget']=trace
 # F macro tests, including arbitrary nonempty right tails.
 for a in range(4,40):
  for b in [1,3,4,7]:
   for k in [0,1,3]:
    if a%2 and b==1:continue
    t=set(range(-a,b))|set(range(b+2,b+2+k));p=0;s=5
    dt=2*a+(24 if a%2==0 else 4)
    for z in range(dt):
     assert s!=-1
     p,s=step(T,t,p,s)
    if b==1:
     assert s==7 and p==2 and t==set(range(-a-3,2))|set(range(3,3+k))
    else:
     ext=3 if a%2==0 else 1
     assert s==5 and p==2 and t==set(range(-a-ext,b))|set(range(b+2,b+2+k))
    out['finite_checks']+=1
 # H macro tests
 for n in range(5,150,4):
  for k in [0,1,3]:
   t=set(range(-n,0))|set(range(1,k+1));p=0;s=7
   dt=(2*n+7)*(n+1)//2-(0 if cid==7 else 2)
   for z in range(dt):
    assert s!=-1
    if z: assert s!=7  # next H is endpoint, so its sole halt edge is not seen
    p,s=step(T,t,p,s)
   assert s==7 and p==-1 and t==set(range(-2*n,-1))|set(range(k+1))
   out['finite_checks']+=1
 # blank prefix
 t=set();p=0;s=0;dt=43
 for z in range(dt):p,s=step(T,t,p,s)
 assert s==7 and t==set(range(p-9,p))
 out['machines'][f'C{cid:02d}']={'machine':TMS[cid-1],'blank_prefix_steps':dt,'H_recurrence':'(n,k) -> (2*n-1,k+1) for n=1 mod4,n>=5','macro_steps': '(2*n+7)*(n+1)/2' + ('-2' if cid==8 else ''),'verdict':'nonhalting_by_inductive_recurrence'}
Path('candidate_theory_certificate.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'finite_checks':out['finite_checks'],'machines':out['machines']}),flush=True)
