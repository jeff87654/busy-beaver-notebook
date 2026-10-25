# X(a,n) chain for F2.11: a>=4 even: (a-2,4n+29); a=2: n%3==2 HALT, n%3==0 -> (2n/3+4,21), n%3==1 -> (2(n-1)/3+4,25)
# start (90,21). Phase from (a,n): k=(a-2)/2 steps -> N with 3N+29 = 4^k (3n+29). Track residues mod 3^P, losing precision per level.
P=400
a,n=90,21; exact=True; level=0
k=(a-2)//2; N=(4**k*(3*n+29)-29)//3   # exact first phase
print('level0 N bits',N.bit_length(),'N%3',N%3)
mod=3**P
while True:
    level+=1
    r=N%3
    if r==2: print('HALT at reload',level,'(N%3==2)'); break
    a=2*(N//3)+4 if r==0 else 2*((N-1)//3)+4; n=21 if r==0 else 25
    # k=(a-2)/2 = N//3 + 1 ; known mod current precision
    k=(N//3)+1          # N known mod 3^p -> N//3 known mod 3^(p-1)
    P-=1; 
    if P<3: print('precision exhausted at level',level); break
    m=3**(P+1)
    T=(pow(4,k% (3**P) + 3**P, m)*(3*n+29))%m   # 4 has order 3^P mod 3^(P+1)
    N=((T-29)//3) % 3**P if (T-29)%3==0 else None
    print('reload',level,'r',r,'next n0',n,'-> N%3',N%3)
    N=N  # residue mod 3^P
