"""Follow the reset recurrence of 1RB1LG_1RC0RE_... 3-adically.
S(n,k,j) = 0^inf A>0 1^n (011)^k 0 0 1^j 0^inf.
S(n,k+1,j) -> S(4n+2,k,j);  S(n,0,j): n%6==4 -> S(4,(n-1)/3,j+1); n%6==0 -> S(14,(n-6)/3,j+1); n%6==2 -> HALT.
From S(n0,K,j): N = ((3 n0 + 2) 4^K - 2)/3.
"""
import sys
M0 = int(sys.argv[1]) if len(sys.argv) > 1 else 400
# exact phase
n0, K, j = 10, 0, 0   # S(10,0,0) at step 40
t = 0
exact = True
mod = None
hist = []
while True:
    if exact:
        N = ((3*n0 + 2) * 4**K - 2) // 3
        assert ((3*n0 + 2) * 4**K - 2) % 3 == 0
        r = N % 6
        hist.append((t, n0, K if K < 10**30 else 'len %d digits' % len(str(K)), r))
        print('reset %d: S(%d, K, %d), K%s -> N mod 6 = %d' % (t, n0, j, ('=%d' % K) if K < 10**30 else (' ~ 10^%d' % (len(str(K))-1)), r))
        if r == 2:
            print('HALT at reset', t, 'N =', N if N < 10**60 else '~10^%d' % (len(str(N))-1)); break
        if r == 4:
            n0, K = 4, (N - 1) // 3
        else:
            n0, K = 14, (N - 6) // 3
        j += 1; t += 1
        if K > 10**6:
            # switch to modular: keep K mod 3^M
            exact = False
            M = M0
            Kr = K % 3**M  # K exact here only if 4**K was computed; see note
            print('switching to 3-adic with M =', M, '; K has', len(str(K)), 'digits')
    else:
        # need Kr mod 3^M, compute next
        # 4^K mod 3^(M+1) requires K mod 3^M: have it. Next K' = ((3n0+2)4^K - c)/9, known mod 3^(M-1)
        m = M + 1
        P = pow(4, Kr, 3**m)      # 4^K mod 3^(M+1)   (ord of 4 mod 3^(M+1) is 3^M)
        A = ((3*n0 + 2) * P - 2) % 3**m   # = 3N mod 3^(M+1)
        # N mod 3^M
        assert A % 3 == 0
        Nm = (A // 3) % 3**M
        r3 = Nm % 3
        # N is even always (K>=1): N mod 6
        r = {0: 0, 1: 4, 2: 2}[r3]
        print('reset %d: S(%d, K, %d), K mod 3 = %d -> N mod 6 = %d   (precision 3^%d)' % (t, n0, j, Kr % 3, r, M))
        if r == 2:
            print('HALT at reset', t); break
        if r == 4:
            n0 = 4; Kr = ((Nm - 1) // 3) % 3**(M-1)
        else:
            n0 = 14; Kr = ((Nm - 6) // 3) % 3**(M-1)
        M -= 1
        j += 1; t += 1
        if M < 3:
            print('precision exhausted'); break
