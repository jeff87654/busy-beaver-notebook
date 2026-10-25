import sys, collections
from dig import step, norm
L,R=[1],[0,3,3,3,3,1]
N=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); S=sys.argv[4]
for i in range(N):
    r,L2,R2=step(L,R)
    if r.startswith('STUCK'): print(r,i,L,R); break
    if a<=i<b and r in S: print(i,r,''.join(map(str,L)).rjust(30),'|',''.join(map(str,R)))
    L,R=norm(L2,R2)
