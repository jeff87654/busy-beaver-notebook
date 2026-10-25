from pathlib import Path
import json, hashlib

machines=Path('discovery_holdouts.txt').read_text().splitlines()
def table(s):
 return [[(int(x[0]),1 if x[1]=='R' else -1,-1 if x[2]=='Z' else ord(x[2])-65) for x in (r[:3],r[3:])] for r in s.split('_')]
def run(T,ones,head,state,steps):
 ones=set(ones)
 for i in range(steps):
  w,d,state=T[state][int(head in ones)]
  if w:ones.add(head)
  else:ones.discard(head)
  head+=d
  if state<0:return ones,head,state,i+1
 return ones,head,state,steps

def predicted(candidate,n,m,suffix):
 k,r=divmod(n,4)
 if r==0: N=9*k+1;word='1'*N+'0'*m+'1'+suffix;dt=18*k*k+23*k+3
 elif r==2:N=9*k+6;word='1'*N+'0'*m+'1'+suffix;dt=18*k*k+41*k+20
 elif r==3:N=9*k+12;word='1'*N+'0'*(m-2)+'1'+suffix;dt=18*k*k+59*k+57
 else:
  N=3 if candidate==5 else 2
  word='1'*N+'0'*(9*k+3)+'1'+'0'*(m-2)+'1'+suffix
  dt=18*k*k+23*k+(22 if candidate==5 else 19)
 return word,dt

def check_word(T,word,dt,expected):
 ones,head,state,t=run(T,{i for i,c in enumerate(word) if c=='1'},-1,0,dt)
 actual={i-head-1 for i in ones};want={i for i,c in enumerate(expected) if c=='1'}
 assert state==0 and t==dt and actual==want,(word[:100],dt,expected[:100],state,head,sorted(actual)[:100])
 return head+1

out={'warning':'Finite checks corroborate the universal phase proof; they do not replace it.','phase_checks':[],'blank_seeds':[],'expansion_checks':[]}
for candidate in (5,6):
 T=table(machines[candidate-1]);count=0
 for n in range(1,81):
  for m in (3,4,5,6,10):
   for suffix in ('','111','00101','0100110011'):
    before='1'*n+'0'*m+'1'+suffix
    after,dt=predicted(candidate,n,m,suffix)
    check_word(T,before,dt,after);count+=1
 out['phase_checks'].append({'candidate':f'C{candidate:02}','cases':count,'status':'pass','n_range':[1,80],'m_values':[3,4,5,6,10],'suffixes':['','111','00101','0100110011']})
 seed=30517 if candidate==5 else 12631
 c,gap,tail,period=(3,327,323,30494) if candidate==5 else(2,210,204,12611)
 word='1'*c+'0'*gap+'1'
 ones,head,state,t=run(T,set(),0,0,seed)
 assert state==0 and {i-head-1 for i in ones}=={i for i,x in enumerate(word) if x=='1'},(candidate,head,state,len(ones))
 out['blank_seeds'].append({'candidate':f'C{candidate:02}','machine':machines[candidate-1],'steps':seed,'head':head,'state':'A','word':'1^%d 0^%d 1'%(c,gap),'ones':len(ones),'status':'pass'})
 for j in range(8):
  before=word+('0'*tail+'1')*j;after=word+('0'*tail+'1')*(j+1)
  shift=check_word(T,before,period,after)
  assert shift==-(tail+1),(candidate,shift)
  out['expansion_checks'].append({'candidate':f'C{candidate:02}','j':j,'steps':period,'shift':shift,'status':'pass'})
Path('unresolved_early_proof_checks.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'phase_checks':out['phase_checks'],'blank_seeds':out['blank_seeds'],'expansion_checks':len(out['expansion_checks'])},indent=2))
