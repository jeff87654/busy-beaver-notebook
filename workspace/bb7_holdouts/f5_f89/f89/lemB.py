from lemma import *
from msim import V, decode, show, next_K
V('a',0); V('k',0); V('d',0); V('c',0); V('m',1); V('n',0); V('p',0)
def isone(x): return x=='1' or (not isinstance(x,str) and x[1]=='1')
import msim
def first(x): return x if isinstance(x,str) else (x[1][0] if msim.lb(x[2])>=1 else None)
def last(x): return x if isinstance(x,str) else (x[1][-1] if msim.lb(x[2])>=1 else None)
def predA(s):
    t,h=s.t,s.h
    return s.q=='A' and h>=1 and h+1<len(t) and t[h]=='1' and first(t[h+1])=='1' and last(t[h-1])=='1'
predA.pred=True
# a = 2a'+1, d = 2d'+3 (>=3), k = k'+1
print('B1',prove('B1','[D]0 0 0 1 01^2*a+1 101^k+5 1 01^2*d+3 1 01^c', predA, '1 [A]1 1 01^2*a+4 1 1 011^k+4 01^2*d+3 1 01^c'))
print('B2',prove('B2','1^m [A]1 1 01^p+4 1 1 011^n+3 01^d 1 01^c', predA, '1^m+3 [A]1 1 01^p+4 1 1 011^n+2 01^d 1 01^c'))
print('B2r2',prove('B2r2','1^m [A]1 1 01^p+4 1 1 011 011 01^d 1 01^c', predA, '1^m+3 [A]1 1 01^p+4 1 1 011 01^d 1 01^c'))
print('B2r1',prove('B2r1','1^m [A]1 1 01^p+4 1 1 011 01^d 1 01^c', predA, '1^m+3 [A]1 1 01^p+4 1 1 01^d 1 01^c'))
for rest in ('1 01^c','1 01^c 1 01^d+1','',):
    items,h,q=build('1^3*k+10 [A]1 1 01^2*a+4 1 1 01^2*d+3 '+rest); s=Sim(items,h,q)
    while True:
        ev=s.run(lambda e,S: e[0]=='Lnew' and e[1]=='D')
        dd=decode(s.t,s.h)
        if dd is not None or ev[0]=='HALT': break
    print('B3 rest',rest,show(dd) if dd else ev)
