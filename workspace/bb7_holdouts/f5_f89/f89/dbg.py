from lemma import *
import msim
from msim import V
V('a',0); V('k',0); V('d',0); V('c',0); V('m',1); V('n',0); V('p',0)
items,h,q=build('1^m [A]1 1 01^p+4 1 1 011^n+3 01^d 1 01^c')
s=Sim(items,h,q)
def show(s):
    return ''.join((c if i!=s.h else '['+s.q+']'+c) if isinstance(c,str) else '|%s^%r|'%(c[1],c[2]) for i,c in enumerate(s.t))
for i in range(400):
    try:
        s.step()
    except Fail as e: print('FAIL',e); break
    print(i, show(s))
