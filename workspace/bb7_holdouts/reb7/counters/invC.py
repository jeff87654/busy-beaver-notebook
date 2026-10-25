import idle, sys
import absC
from absC import refill
# abstract run with accelerated run-down; track min (b-K) at borrows and top rebuilds. y kept exact while < 2^LIM, else symbolic 'BIG'
LIM=10**5
def run(R,y,N,newtop=None):
    absC.NEWTOP=newtop
    minslack=None; ev=0; tops=0
    while ev<N:
        ev+=1
        if R[-1]>=2 and R[-1]%2==0:
            v=R[-1]//2; R[-1]=0
            if y.bit_length()+v>LIM: return 'BIGY',ev,minslack,tops,R[:12]
            y=(y+5)*(1<<v)-5; continue
        b=(y-1)//2
        n=len(R); i=n-1
        while i>=1 and R[i] in (0,1): i-=1
        top = (i==0 and R[0]==1)
        B=R[i+1:]
        out,K,pos=refill(B,top)
        sl=b-K
        minslack=sl if minslack is None else min(minslack,sl)
        if top:
            tops+=1
            if b-2-K<1: return 'SMALLTOP',ev,minslack,tops,R[:12]
            if b>10**6: return 'TOPBIG b~2^%d len would be ~b'%b.bit_length(),ev,minslack,tops,R[:12]
            R=[newtop if newtop else R[0]]+[2]*(b-2-K)+[3]+out
        else:
            if b<=K: return 'SMALL',ev,minslack,tops,R
            R[i]-=2; out[0]=2*(b+1-K)+B[0]; R=R[:i+1]+out
        y=7
    return 'N',ev,minslack,tops,R[:12]
print(run([1,0],19,10**6))
print(run([1,0],19,10**6,5))
print(run([1,0,0,0],51,10**6))
