from dig import step
Q=[1,0,1,1]; T=[2,2]
for k in range(0,4):
  for j in range(0,4):
    for z0 in range(0,12):
      L=Q+[0]*z0; R=[3,3]+[3]*k+[0]*j+[0]+T
      n=0; out=None
      while n<10**7:
        r,L,R=step(L,R); n+=1
        if r.startswith('STUCK'): out='stuck'; break
        if len(L)<len(Q) or L[:len(Q)]!=Q: out='touchQ'; break
        if R[-2:]==T and R[0]==0 and R[-3]==1 and all(d==3 for d in R[1:-3]) and L[-1]==1:
          out='S: L=Q+%s i=%d'%(L[len(Q):],len(R)-4); break
      print('k',k,'j',j,'z0',z0,out,n)
