import sys; sys.path.insert(0,'.'); from chk import first
M='1RB0LB_1LC0RH_1RG1LD_0LE---_1RF1LE_1LA1LF_0RE0RC_1RG1RH'
ok=bad=0
for a in range(3,40,3):
  for b in range(4,40,3):
    r=first(M,'L','A','A',0,'0 1^%d 0 1^%d 0110101'%(a,b),steps=10**7)
    exp='[A]0 (1)^%d 0 (1)^%d 0 1 1 0 1 0 1'%(a+3,b-1) if b-1>=3 else None
    if r==exp: ok+=1
    else: bad+=1; print(a,b,r,exp)
print(M,'ok',ok,'bad',bad)
