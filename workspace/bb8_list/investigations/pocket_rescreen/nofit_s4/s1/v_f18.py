import sys
from val import *
m=open('/dev/stdin').read().strip() if False else None
import subprocess
m0='1RB1RG_1RC0LD_0RD1RD_0LE1RC_1LF0RG_1LB1LF_1RE1RH_---0RA'
m='_'.join(''.join(t[i:i+3].replace('L','x').replace('R','L').replace('x','R') for i in (0,3)) for t in m0.split('_'))
cj=lambda x,y,T: x%2==1 and T in ('011111','0111','01','')
br=lambda R: bounce_round(m,'D',R,'1','1',pre='00',mid='0',canjump=cj,maxev=3000)
bad=n=0
nxt={'011111':('0111',4),'0111':('01',4),'01':('',8),'':('011111',11)}
for y in range(4,200):
    for T in ('011111','0111','01',''):
        if T=='' and y%3: continue
        R='001110'+'1'*y+T
        got=br(R); T2,c=nxt[T]; exp=(3,2*y+c,T2); n+=1
        if got!=exp:
            bad+=1
            if bad<10: print('MISMATCH',y,repr(T),str(got)[:70],exp)
print(n,'cases',bad,'bad')
