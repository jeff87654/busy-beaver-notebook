"""Follow the reset recurrence of 1RB0LF_1RC0RE_1LD1LC_1LA0LD_1LB1RA_1RG1LG_0LH0RD_---1RF 3-adically.
S(n,k,j) = 0^inf A>0 1^n (001)^k 000 1^j 0^inf.
digit: S(n,k+1,j) -> S(4n+2,k,j) (n even)
reset on S(n,0,j): n%6==4 -> S(1,(n-1)/3,j+1) -> S(10,(n-4)/3,j+1) (two O rules);
                   n%6==2 -> S(8,(n-5)/3,j+1);   n%6==0 -> HALT.
From S(n0,K,j): N = ((3 n0 + 2) 4^K - 2)/3.
"""
import sys
M0 = int(sys.argv[1]) if len(sys.argv) > 1 else 400
n0, K, j = 10, 0, 0   # S(10,0,0) at step 48
t = 0
exact = True
while True:
    if exact:
        N = ((3*n0 + 2) * 4**K - 2) // 3
        assert ((3*n0 + 2) * 4**K - 2) % 3 == 0
        r = N % 6
        print('reset %d: S(%d, K, %d), K%s -> N mod 6 = %d' % (t, n0, j, ('=%d' % K) if K < 10**30 else (' ~ 10^%d' % (len(str(K))-1)), r))
        if r == 0:
            print('HALT at reset', t, 'N =', N if N < 10**60 else '~10^%d' % (len(str(N))-1)); break
        if r == 4:
            n0, K = 10, (N - 4) // 3
        else:
            n0, K = 8, (N - 5) // 3
        j += 1; t += 1
        if K > 10**6:
            exact = False
            M = M0
            Kr = K % 3**M
            print('switching to 3-adic with M =', M, '; K has', len(str(K)), 'digits; K mod 27 =', K % 27)
    else:
        m = M + 1
        P = pow(4, Kr, 3**m)      # 4^K mod 3^(M+1); ord of 4 mod 3^(M+1) is 3^M
        A = ((3*n0 + 2) * P - 2) % 3**m
        assert A % 3 == 0
        Nm = (A // 3) % 3**M
        r = {0: 0, 1: 4, 2: 2}[Nm % 3]
        print('reset %d: S(%d, K, %d), K mod 3 = %d -> N mod 6 = %d   (precision 3^%d)' % (t, n0, j, Kr % 3, r, M))
        if r == 0:
            print('HALT at reset', t); break
        if r == 4:
            n0 = 10; Kr = ((Nm - 4) // 3) % 3**(M-1)
        else:
            n0 = 8; Kr = ((Nm - 5) // 3) % 3**(M-1)
        M -= 1
        j += 1; t += 1
        if M < 3:
            print('precision exhausted'); break
