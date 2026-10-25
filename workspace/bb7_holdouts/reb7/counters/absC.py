import idle, random, sys
from rlp import rl
# abstract one-event map for family C (rep orientation): state = raw runs R (digits) + y (odd), at a=0 moments.
NEWTOP=None
TOPOFF=0
def refill(B,first_after_flag):
    out=[];prevF=first_after_flag;K=0;pos=[]
    for e in B:
        f=e  # raw 0 or 1
        if prevF: out.append(0+f)
        else: out.append(2+f); K+=1; pos.append(len(out)-1)
        prevF=(f==1)
    return out,K,pos
def step(R,y):
    R=list(R); b=(y-1)//2
    if R[-1]>=2 and R[-1]%2==0:
        R[-1]-=2; return R,2*y+5
    if R[-1]%2==1: return None,'LASTODD'
    n=len(R); i=n-1
    while i>=1 and R[i] in (0,1): i-=1
    if i==0 and R[0]==1: return None,'TOP'
    B=R[i+1:]
    out,K,pos=refill(B,False)
    if b<=K: return None,'SMALL'
    R[i]-=2
    out[0]=2*(b+1-K)+B[0]
    return R[:i+1]+out,7
def step_top(R,y):
    b=(y-1)//2; B=R[1:]
    out,K,pos=refill(B,True)
    j=b-2-K+TOPOFF
    if j<1: return None,'SMALLTOP'
    return [NEWTOP if NEWTOP else R[0]]+[2]*j+[3]+out,7
def astep(R,y):
    r=step(R,y)
    if r[0] is None and r[1]=='TOP': return step_top(R,y)
    return r
def fmt(R,y):
    o=[];i=0;L=R+[0,y]
    while i<len(L):
        j=i
        while j<len(L) and L[j]==L[i]: j+=1
        o.append(str(L[i])+('x%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(o)
if __name__=='__main__':
    M=sys.argv[1]; O=sys.argv[2]; Q=sys.argv[3]; n=int(sys.argv[4])
    if len(sys.argv)>5: NEWTOP=int(sys.argv[5])
    random.seed(7); bad=0; tot=0
    for it in range(n):
        L=random.randint(1,6)
        R=[random.choice([1,3,5,7])]+[random.choice([0,2,4,6,0,0,1,3,5]) for _ in range(L)]
        # flags never last
        if R[-1]%2==1: R[-1]-=1
        y=2*random.randint(L+3,L+20)+1
        a=astep(R,y)
        if a[0] is None: continue
        lit=rl(M,O,Q,R+[0,y],10**8,1,0)[0]
        got=lit.split('|')[1].strip() if '|' in lit else lit
        exp=fmt(*a)
        tot+=1
        if got!=exp:
            bad+=1; print('MISMATCH',fmt(R,y),'exp',exp,'lit',lit)
    print('tot',tot,'bad',bad)
