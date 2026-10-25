# digit-level abstract system: L list (top last), R list (head first). implicit zeros beyond ends.
import sys
def step(L,R):
    def r(i): return R[i] if i<len(R) else 0
    if r(0)==3 and r(1)>=1: return 'R1', L+[0], [3,r(1)-1]+R[2:]
    if r(0)==3 and r(1)==0: return 'R2', L+[1], [0,1]+R[2:]
    if r(0)==0 and r(1)==3 and r(2)>=1: return 'R4', L+[1], [3,r(2)-1]+R[3:]
    if r(0)==0 and r(1)==1:
        j=len(L); 
        while j>0 and L[j-1]==1: j-=1
        n1=len(L)-j
        if n1%2==0: return 'STUCK-EVEN',L,R
        LL=L[:j]+[0,0,0]  # implicit zeros
        if LL[j]!=0 or LL[j-1 if j>0 else 0]!=0: pass
        a=L[j-1] if j>=1 else 0; b=L[j-2] if j>=2 else 0
        if a!=0 or b!=0: return 'STUCK-Z',L,R
        m=(n1-1)//2; Lp=L[:max(j-2,0)]
        if r(2)>=1: return 'R3', Lp, [3]*(m+2)+[r(2)-1]+R[3:]
        e=Lp[-1] if Lp else 0
        Lq=(Lp[:-1] if Lp else [])+[e+1]
        return 'R5', Lq, [0]+[3]*(m+1)+[1]+R[3:]
    return 'STUCK',L,R
def norm(L,R):
    L=list(L); R=list(R)
    while L and L[0]==0: L.pop(0)
    while R and R[-1]==0: R.pop()
    return L,R
