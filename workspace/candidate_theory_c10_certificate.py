"""Exact transcription checks for the universal C10 sweep lemmas."""
import json
from pathlib import Path
from sim import parse
T=parse(Path('discovery_holdouts.txt').read_text().splitlines()[9])
def C(a,b):
 w='1111'+'01'*a+'0'+'1'*b+'01';return w,len(w),7
def D(n):return '1'*n,n,7
def E(n):return '1'*n+'01',n+2,7
def P(u,k,v):
 pre='1111'+'01'*u;return pre+'01'*k+'1'+'01'*v+'1',len(pre)-1,4
def R(k,v):return '1111'+'01'*k+'1'+'01'*v+'1',4,7
def advance(config,steps):
 w,p,s=config;t={i for i,c in enumerate(w)if c=='1'}
 for j in range(steps):
  assert s!=-1
  wr,d,ss=T[s][int(p in t)]
  if wr:t.add(p)
  else:t.discard(p)
  p+=d;s=ss
 lo=min(t);hi=max(t);return ''.join('1'if i in t else'0'for i in range(lo,hi+1)),p-lo,s
checks={}
def check(name,src,dst,steps):
 actual=advance(src,steps)
 assert actual==dst,(name,src,actual,dst)
 checks[name]=checks.get(name,0)+1
for a in range(1,7):
 for b in range(1,22,2):check('C_entry',C(a,b),P(a-1,1,(b+3)//2),b+14)
for u in range(1,7):
 for k in range(1,10):
  for v in range(1,7):check('P_interior',P(u,k,v),P(u-1,k+2,v-1),6*k+8)
  w='1111'+'01'*(u-1)+'1'*(2*k+2)+'01'
  check('P_v0',P(u,k,0),(w,len(w),7),4*k+5)
for k in range(1,10):
 for v in range(0,7):check('P_boundary',P(0,k,v),R(k+2,v),19)
 for v in range(1,7):check('R_interior',R(k,v),R(k+3,v-1),6*k+22)
 check('R_terminal',R(k,0),E(2*k+4),4*k+2)
for n in range(4,100,2):
 check('D_return',D(n),C(n//2-2,1),2*n+16)
 check('E_return',E(n),D(n+10),6*n+51)
check('blank_prefix',('',0,0),D(8),39)
# The mathematical induction depends on universal sweep proofs, not this finite grid.
proof=Path('candidate_audit_c10.md')
result={'machine':Path('discovery_holdouts.txt').read_text().splitlines()[9],'verdict':'nonhalting_by_inductive_recurrence','proof_documents':['candidate_audit_c10.md','candidate_theory_c10.md'],'finite_check_counts':checks,'finite_checks_total':sum(checks.values()),'all_checks_passed':True,'outer_initial_a':2,'outer_formula':'a_j=(32*2^j-2*j-17-7*(-1)^j)/4','halting_boundaries':'S_j=6*2^j-j-6','proof_basis':'Universal P/R/D/E sweep lemmas plus strict interval invariance; finite checks detect transcription mistakes.'}
Path('candidate_theory_c10_certificate.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
