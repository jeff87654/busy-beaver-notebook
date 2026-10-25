from rewrite import Rope,advance
for u in [2,3,4,5,10,20]:
 a=4;r=Rope([('010',u),('011',1),('100',10),('110',1),('010',10),('01001100101001',1)])
 for i in range(20):a,r,t,rule=advance(a,r)
 raw=r.string().rstrip('0');z=Rope([(raw,1)])
 uv=z.run('010');p=z.peek(3);z.drop(3);v=z.run('100');p2=z.peek(3);z.drop(3);w=z.run('010')
 print(u,'->',a,uv,p,v,p2,w,z.string())
