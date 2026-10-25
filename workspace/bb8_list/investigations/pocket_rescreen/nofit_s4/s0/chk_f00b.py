import sys; sys.path.insert(0,'.'); from chk import first
M='1RB0LF_1LC1RG_0LD1LC_1RE1LF_1RA1RE_1LE1LD_0LD1RH_---0RE'
ok=bad=0
for a in range(1,40):
  for b in range(3,7):
    r=first(M,'L','F','F',0,'0 1^%d 0 1^%d'%(a,b))
    exp='[F]0 (1)^%d 0 (1)^%d'%(2*a+8,b-1) if b-1>=3 else '[F]0 (1)^%d 0 1 1'%(2*a+8)
    if r==exp: ok+=1
    else: bad+=1; print(a,b,r,exp)
print('ok',ok,'bad',bad)
