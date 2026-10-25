import idle
from nx import nxt,M1,M2
for M in (M1,M2):
  for k in range(1,5):
    for d in (1,2,3):
      for b in range(0,7):
        y=2*b+2
        r=[3,3,d,2*k+5,y]
        e=nxt(M,r)
        print(M[-6:],'k',k,'d',d,'b',b, r,'->',e[1] if e[0]=='E' else e)
