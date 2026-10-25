from dig import step
def reach(L,R,tL,tR,Q):
    n=0
    while n<10**7:
        if L==tL and R==tR: return n
        r,L,R=step(L,R); n+=1
        if r.startswith('STUCK') or L[:len(Q)]!=Q: return None
    return None
bad=0
for Q in ([1,0,1,1],[1,1],[1,0,1,0,1]):
 for k in range(0,4):
  for j in range(1,4):
   for z in range(0,3):
    for u in (0,1,2):
      T=[2,1]
      n=reach(Q+[0]*(z+3*j-1),[3,3]+[3]*k+[0]*j+[u+1]+T,Q+[0]*z,[3,3]+[3]*(k+j)+[u]+T,Q)
      if n is None: bad+=1; print('Z fail',Q,k,j,z,u)
   for z in range(0,3):
      T=[0,2,1]
      n=reach(Q+[0]*(z+3*j),[3,3]+[3]*k+[0]*j+[0]+T,Q+[0]*z+[1],[0]+[3]*(k+j+1)+[1]+T,Q)
      if n is None: bad+=1; print('W fail',Q,k,j,z)
print('bad',bad)
