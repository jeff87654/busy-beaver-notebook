from rewrite import Rope,advance,advance_fast

def eq(r,s):
 r=Rope(r.d);s=Rope(s.d)
 while r.d and s.d:
  a,n=r.d[0];b,m=s.d[0];L=min(len(a)*n,len(b)*m)
  if any(a[i%len(a)]!=b[i%len(b)] for i in range(min(L,len(a)*len(b)))):return False
  for z in [r,s]:
   w,c=z.d.popleft();rem=len(w)*c-L;q,k=divmod(rem,len(w))
   if q:z.d.appendleft([w,q])
   if k:z.prepend(w[-k:])
 return not r.d and not s.d

a=4;r=Rope([('110100100',1)]);t=189
for i in range(240):
 aa,rr,tt,rule=advance_fast(a,Rope(r.d))
 if rule.startswith('cycle'):
  print('TEST',i,rule,'a',a,'tail',repr(r)[:300])
  m=int(rule.split('^')[1]);t0=0
  for j in range(m):
   z=Rope(r.d);u=z.run('010');z.drop(3);v=z.run('100');z.drop(3);w=z.run('010')
   pred=Rope([('010',9*u+52),('011',1),('100',v-3),('110',1),('010',w-1)])
   for part,n in z.d:pred.append(part,n)
   tj=0
   for k in range(20):a,r,dt,_=advance(a,r);tj+=dt
   if a!=4 or not eq(r,pred) or tj!=180*u*u+2436*u+12*v+8072:
    print('MISMATCH CYCLE',j,'v',v,'w',w,'a',a,'same',eq(r,pred),'time delta',tj-(180*u*u+2436*u+12*v+8072));break
   t0+=tj
  else:print('ALL MATCH',m,'time',t0==tt,'end',eq(r,rr))
  break
 a,r,dt,rule=advance(a,r);t+=dt
