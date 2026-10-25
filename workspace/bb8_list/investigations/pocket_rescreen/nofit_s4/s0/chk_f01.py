import sys; sys.path.insert(0,'.'); from chk import first
Ms=['1RB0RA_1LC1RE_1LD0LB_0RE0RF_0LA0LF_1RD0RG_1RF0RH_0LD---','1RB0RA_1LC1RE_1LD0LB_0RE0RH_0LA0LF_1RD0RG_1RF---_1RD1RC','1RB0RA_1LC1RE_1LD0LB_0RE0RF_0LA0LF_1RD0RG_1RF0RH_0LA---','1RB0RA_1LC1RE_1LD0LB_0RE0RF_0LA0LF_1RD0RG_1RF1RH_1LC---']
for M in Ms:
  ok=bad=0
  for n in range(1,241,2):
    r=first(M,'L','B','B',0,'0 01^%d'%n)
    exp='[B]0 (01)^%d'%(3*n+2) if 3*n+2>=3 else None
    if r==exp: ok+=1
    else: bad+=1; print(n,r,exp)
  print(M,'ok',ok,'bad',bad)
