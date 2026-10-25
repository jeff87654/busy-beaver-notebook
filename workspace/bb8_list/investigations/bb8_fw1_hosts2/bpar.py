import idle, sys
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\counters')
# family B: exact check of round formula on small lists, then 2-adic ABSORB sequence
def run_list(c,R,y,maxit=10**6):
    # exact abstract run (absB rules) until ABSORB moment ([c|1] y=5); returns c or None
    R=list(R)
    for _ in range(maxit):
        if len(R)==1: return c
        if R[-1]>=2: 
            if R[-1]>40: return 'BIG'
            y=(y+7)*2**(R[-1]//2)-7; R[-1]=0; continue
        n=len(R); i=n-1
        while i>=1 and R[i]==0: i-=1
        K=n-1-i
        if i==0:
            c=(c if c is not None else -1)+y+2-2*K; R=[1]+[2]*(K-1); y=5; continue
        R[i]-=2; R=R[:i+1]+[y+3-2*K]+[2]*(K-1); y=5
    return 'MAX'
print('n=1:',run_list(None,[1,2],5),'(expect -1+17=16)')
print('n=2:',run_list(None,[1,2,2],5),'(expect -1+6152=6151)')
def absorb_seq(c,M=3000,rounds=60):
    out=[]; mod=1<<M
    for r in range(rounds):
        odd=c%2; n=(c-odd)//2+5; c0=1 if odd else -1
        out.append((r,odd,M))
        c=(c0+6168-n*(n+6))%(1<<(M-1)); M-=1
    return out
c1=int(sys.argv[1]) if len(sys.argv)>1 else 16
s=absorb_seq(c1)
print('ABSORB parities from c1=%d:'%c1,''.join(str(o) for _,o,_ in s))
