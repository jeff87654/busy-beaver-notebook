from symsim import *
import sys
one,n=prove('bounceA1','000 [A0] 0 (100)^{j} 1010 (110)^{k+1}','[A0] 0 (100)^{j+2} 1010 (110)^{k}',{'j':0,'k':0})
print('bounceA1 proven',n)
bA=Lemma('bounceA*','[A0] 0 (100)^{j} 1010 (110)^{k}','[A0] 0 (100)^{j+2k} 1010',{'j':0,'k':1},walled=(False,True))
c=make_config('[A0]')
n=0
lim=int(sys.argv[1])
while n<lim:
    if bA.apply(c):
        print(n,'LEMMA',c.steps if not c.sym_steps else '?',c)
    else:
        c.step(); c.normalize()
    n+=1
    if not c.left: print(n, c)
