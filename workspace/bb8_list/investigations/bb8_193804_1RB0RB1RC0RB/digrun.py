import sys, collections
from dig import step, norm
L,R=[1],[0,3,3,3,1]
N=int(sys.argv[1])
cnt=collections.Counter(); maxd=0; lens=[]
for i in range(N):
    r,L2,R2=step(L,R)
    if r.startswith('STUCK'): print(r,i,L,R); break
    cnt[r]+=1
    if max(L2+[0])>1 or max(R2+[0])>3: print('BIGDIGIT',i,r,L2,R2); break
    L,R=norm(L2,R2)
    if i%(N//20)==0: print(i,''.join(map(str,L)),'|',''.join(map(str,R)))
print(cnt)
