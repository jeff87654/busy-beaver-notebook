from rewrite import Rope,advance
import random,sympy as sp

def cycle(u,v,w,suffix='0111100101001'):
 a=4;r=Rope([('010',u),('011',1),('100',v),('110',1),('010',w),(suffix,1)]);t=0
 for i in range(20):a,r,dt,rule=advance(a,r);t+=dt
 expect=Rope([('010',9*u+52),('011',1),('100',v-3),('110',1),('010',w-1),(suffix,1)])
 return a==4 and r.string().rstrip('0')==expect.string().rstrip('0'),t
for v in range(3,10):
 for w in range(1,4):
  ok,t=cycle(3,v,w)
  if not ok:print('FAIL',v,w)
terms=lambda u,v,w:[u*u,u*v,u*w,v*v,v*w,w*w,u,v,w,1]
rng=random.Random(23);eq=[];ys=[]
for _ in range(30):
 u=rng.randrange(1,20);v=rng.randrange(3,30);w=rng.randrange(1,30)
 ok,t=cycle(u,v,w)
 assert ok,(u,v,w)
 eq.append(terms(u,v,w));ys.append(t)
x=sp.linsolve((sp.Matrix(eq),sp.Matrix(ys)));print(x)
