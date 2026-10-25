from dig import step
Q=[1,0,1,1]
for k in range(0,5):
  for u in [1,2]:
    for z0 in range(0,5):
      L=Q+[0]*z0; R=[3,3]+[3]*k+[0,u,2]
      n=0
      while n<10**7:
        r,L,R=step(L,R); n+=1
        if r.startswith('STUCK'): print('k',k,'u',u,'z0',z0,'stuck',L,R); break
        if R==[3,3]+[3]*k+[3,u-1,2] and L[:len(Q)]==Q and all(c==0 for c in L[len(Q):]):
          print('k',k,'u',u,'z0',z0,'-> z',len(L)-len(Q),'steps',n); break
        if len(L)<len(Q) or L[:len(Q)]!=Q: print('k',k,'u',u,'z0',z0,'touched Q',n,L,R); break
