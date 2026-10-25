from boundary import run
for j in range(16):
 p=f'{j:04b}'
 rows=[]
 for a in [2,3,4]:
  n,t,w=run(a,'101'+p+'001100101001')
  rows.append((a,n,t,w))
 print(p,rows)
