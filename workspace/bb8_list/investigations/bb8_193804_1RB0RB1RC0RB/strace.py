import sys
from dig import step
j=int(sys.argv[1])
L=['P',1]; R=[0]+[3]*j+[1,'T']
# symbolic: treat 'P' and 'T' as opaque; step on lists with sentinel
def st(L,R):
    # strip sentinels for step; ensure step doesn't look into them
    Lr=L[1:]; Rr=R[:-1]
    r,L2,R2=step([9,9,9]+Lr if False else Lr,Rr)
    return r,L2,R2
Lr=[1]; Rr=[0]+[3]*j+[1]
for i in range(100000):
    s=''.join(map(str,Lr)); t=''.join(map(str,Rr))
    print(i, ('P'+s).rjust(25),'|',t+'T')
    if Lr==[1,1,1] and Rr==[0]+[3]*(j-1)+[1]: break
    # guard: R must not be exhausted, L must not underflow
    r,Lr,Rr=step(Lr,Rr)
    print('   ',r)
