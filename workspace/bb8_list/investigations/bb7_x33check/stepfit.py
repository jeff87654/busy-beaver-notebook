import idle, random
from rules import *
random.seed(7)
# D: vary d, b, prefix
cfgs=[]; meta=[]
for _ in range(200):
    pre=[random.randint(0,9) for _ in range(random.randint(0,5))]
    d=random.randint(1,50); b=random.randint(0,300)
    cfgs.append((pre+[d],b)); meta.append(('D',d,b,0))
for _ in range(400):
    pre=[random.randint(1,9) for _ in range(random.randint(0,4))]
    y=random.randint(1,30); k=random.randint(1,14); b=random.randint(2*k-2, 2*k+300)
    cfgs.append((pre+[y]+[0]*k,b)); meta.append(('B',y,b,k))
res=literal(X,cfgs,10**9)
rows=[(m_[0],m_[1],m_[2],m_[3],r[-1]) for m_,r in zip(meta,res)]
D=[r for r in rows if r[0]=='D']
print('D steps - (2b+10): ', set(r[4]-(2*r[2]+10) for r in D))
B=[r for r in rows if r[0]=='B']
import numpy as np
# fit steps ~ poly in b,k : try basis 1,b,k,b*k,k^2,b^2
A=np.array([[1,r[2],r[3],r[2]*r[3],r[3]**2,r[2]**2, r[1]] for r in B],float); y=np.array([r[4] for r in B],float)
c,*_=np.linalg.lstsq(A,y,rcond=None); print('B fit [1,b,k,bk,k2,b2,y]',np.round(c,4),'maxerr',max(abs(A@c-y)))
