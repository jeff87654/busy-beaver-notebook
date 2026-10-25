from lemma import *
from msim import V, decode, show
V('x',1); V('m',2); V('n',0)
RC=lambda e,S: e[0]=='Rnew' and e[1]=='C'
print('S1',prove('S1','[D]0 0 0 1 01^x', RC, '1 1 0 0 10^x 1 [C]0'))
print('S2',prove('S2','1^m 0 0 10^n+1 1 [C]0', RC, '1^m+3 0 0 10^n 1 [C]0'))
items,h,q=build('1^3*x+2 0 0 1 [C]0'); s=Sim(items,h,q)
while True:
    ev=s.run(lambda e,S: e[0]=='Lnew' and e[1]=='D')
    d=decode(s.t,s.h)
    if d is not None or ev[0]=='HALT': break
print('S3',show(d) if d else ev, s.steps)
