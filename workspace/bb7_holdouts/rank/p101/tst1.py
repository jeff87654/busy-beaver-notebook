import idle
from nx import nxt,M1,M2
for M in (M1,M2):
  print(M)
  for n in range(1,7):
    for b in range(0,9):
      r=[2,2*n+2,2*b+2]; e=nxt(M,r)
      print(' E n',n,'b',b,'->',e[1] if e[0]=='E' else e)
  for Y in range(1,16):
      e=nxt(M,[Y]); print(' single',Y,'->',e[1] if e[0]=='E' else e)
