import sys; sys.path.insert(0,'.'); from chk import first
Ms=['1RB0LF_0LC1LG_1RF1RD_0RE---_0RC0RG_1LA0RC_0LA0LH_1RB0LB','1RB0LF_0LC1LG_1RF1RD_0RE---_0RC0RG_1LA0RC_0LA0LH_0RG0LB','1RB0LF_0LC1LG_1RF1RD_0RE---_0RC0RG_1LA0RC_0LA0LH_1RD0LB']
for M in Ms:
  ok=bad=0
  for x in range(4,30,3):
    for y in range(3,40,3):
      L=6+3+2*x+1+2*y
      r=first(M,'R','F','F',L,'10^3 010 01^%d 0 01^%d 0'%(x,y),steps=10**7)
      exp='(10)^3 0 1 0 (01)^%d 0 (01)^%d [F]0'%(x-1,y+2)
      if r==exp: ok+=1
      else: bad+=1; print(x,y,r,exp)
  print(M,'ok',ok,'bad',bad)
