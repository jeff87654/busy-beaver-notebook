from rewrite import Rope,advance
from probe import compact
a=4;r=Rope([('010',2),('011',1),('100',9),('110',1),('010',3),('0111100101001',1)])
for i in range(20):
 a,r,dt,rule=advance(a,r)
 print(i+1,rule,a,dt,compact(r.string()))
