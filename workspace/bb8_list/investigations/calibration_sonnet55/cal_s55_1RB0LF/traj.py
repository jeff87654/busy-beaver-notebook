# S(n,k,j): digit n->4n+2 ; reset: n%6==2 -> S(8,(N-8)/3,j+1); n%6==4 -> S(10,(N-4)/3,j+1); 0 -> halt
m=400; M=3**m
n0,k,j=8,55,2
kk=k; prec=None
for r in range(1,400):
    # N = ((3 n0+2) 4^k - 2)/3 mod 3^(m-r+...)
    modk=3**(m-r)   # k known mod modk (approx)
    P=3**(m-r+1)
    N=(((3*n0+2)*pow(4,kk%modk,3*modk)-2)) # mod 3*modk
    assert N%3==0
    N=(N//3)%modk
    res=N%6 if False else None
    # N even? n0 even -> N even; N mod 3 = N%3; N mod 2=0
    r3=N%3
    resid={0:0,1:4,2:2}[r3]  # even & N%3 -> mod 6
    print(r, j, 'k mod 3 =',kk%3, 'N mod 6 =',resid)
    if resid==0: print('HALT at reset',r,'with j=',j); break
    if resid==2: n0=8; kk=(N-5)
    else: n0=10; kk=(N-4)
    kk=(kk//3)   # exact division: N-8 divisible by 3 as integer mod modk -> kk known mod modk/3
    j+=1
    m2=m-r
