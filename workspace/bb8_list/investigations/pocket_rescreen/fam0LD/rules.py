import sys,random
from probe import step
def pred(L):
    if len(L)==1:
        c=L[0]
        if c%3==1: return 'H'
        return [2]+[1]*(2*(c//3)+(1 if c%3==2 else 0))+[0,0]
    b,a=L[0],L[1]; X=L[2:]
    if a>=1: return [b+2,a-1]+X
    if not X: return [b+2]
    if X[0]>=1: return [1,b+2,X[0]-1]+X[1:]
    if len(X)==1: return [1,b+2]
    if X[1]==0: return [1,b+2]+X[2:]
    return [1,b+2+X[1]]+X[2:]
if __name__=='__main__':
    M=sys.argv[1]; n=int(sys.argv[2]); random.seed(int(sys.argv[3]))
    bad=0
    for t in range(n):
        r=random.random()
        if r<0.1: L=[random.randint(0,60)]
        else:
            L=[random.randint(0,40),random.choice([0,0,0,random.randint(1,20)])]+[random.choice([0,0,1,1,2,random.randint(0,6)]) for _ in range(random.randint(0,8))]
        p=pred(L); s=step(L,M,maxn=10**6)
        got='H' if s[0]=='H' else (s[1] if s[0]=='K' else s)
        if got!=p:
            bad+=1
            if bad<=8: print('MISMATCH',L,'pred',p if p=='H' else p[:12],'got',got if not isinstance(got,list) else got[:12])
    print('tested',n,'bad',bad)
