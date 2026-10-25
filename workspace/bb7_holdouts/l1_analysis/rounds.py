from rewrite import Rope,advance
for n in range(0,31):
 a=2;tail=Rope([('0',1),('1100',n),('101001',1)]);t=0
 try:
  for i in range(10000):
   a,tail,dt,r=advance(a,tail);t+=dt
   if a is None:
    print(n,'HALT','steps',t,'rules',i+1);break
   if r=='blank':
    print(n,'REBUILD',[(w,c) for w,c in tail.d],'steps',t,'rules',i+1);break
   if a.bit_length()>2000:
    print(n,'BIG',i,a.bit_length());break
  else:print(n,'BUDGET',a.bit_length(),len(tail.d))
 except Exception as e: print(n,type(e).__name__,str(e)[:180])
