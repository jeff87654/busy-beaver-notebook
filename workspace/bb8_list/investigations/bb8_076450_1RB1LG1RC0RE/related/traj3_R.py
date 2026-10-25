"""Follow the Z-level recurrence of R1 / R2 exactly, then 3-adically, until the halting class is hit.

R1: Z(n) = 0^inf A>0 1^n 0^inf, n even.       Z(10) at step 40.
    n = 6q+2 (q>=1) -> (26*4^q + 22)/3   in T(q) = 5408*16^q/135 - 1066*4^q/27 + 896q/9 + 5374/45 steps
    n = 6q+4 (q>=1) -> (32*4^q + 22)/3   in T(q) = 8192*16^q/135 - 1312*4^q/27 + 896q/9 + 6116/45 steps
    n = 6q   (q>=1) -> halting config  0^inf G>0 (100)^(2q-1) 111 0000 1 0^inf  after 24q+5 steps
R2: Z(n,j) = 0^inf A>0 1^n 0000 1^j 0^inf.     Z(10,0) at step 40.
    n = 6q+4 (q>=1) -> (26*4^q + 4)/3,  j+1   in 5408*16^q/135 - 2002*4^q/27 + 896q/9 + 4009/45 steps
    n = 6q   (q>=2) -> (110*4^(q-1) + 4)/3, j+1 in 1210*16^q/27 - 4235*4^q/54 + 896q/9 + 2035/9 steps
    n = 6q+2        -> halting config  0^inf G>0 (100)^(2q) 01 0000 1^(j+1) 0^inf  after 24q+13 steps

n is always even, so n mod 6*3^k is determined by n mod 3^(k+1).  In modular mode we keep n mod 3^K;
q = (n-r)/6 is then known mod 3^(K-1), which determines 4^q mod 3^K (ord of 4 mod 3^K is 3^(K-1)), hence
n' mod 3^(K-1): one 3-adic digit is lost per reset.
usage: python traj3_R.py R1|R2 [K0=400] [EXACT_DIGITS=200000]
"""
import sys
sys.set_int_max_str_digits(0)
from fractions import Fraction
from math import log10

M = sys.argv[1]
K0 = int(sys.argv[2]) if len(sys.argv) > 2 else 400
EXD = int(sys.argv[3]) if len(sys.argv) > 3 else 200000
L4 = log10(4)

if M == 'R1':
    RULE = {2: (26, 22, 0), 4: (32, 22, 0)}; HALTCLASS = 0
    TSTEP = {2: lambda q: Fraction(5408 * 16**q, 135) - Fraction(1066 * 4**q, 27) + Fraction(896 * q, 9) + Fraction(5374, 45),
             4: lambda q: Fraction(8192 * 16**q, 135) - Fraction(1312 * 4**q, 27) + Fraction(896 * q, 9) + Fraction(6116, 45)}
    LEAD = {2: 5408 / 135, 4: 8192 / 135}          # T ~ LEAD * 16^q
    HSTEPS = lambda q: 24 * q + 5
    HONES = lambda q, j: 2 * q + 3                    # (100)^(2q-1) 111 0000 1
else:
    RULE = {4: (26, 4, 0), 0: (110, 4, 1)}; HALTCLASS = 2
    TSTEP = {4: lambda q: Fraction(5408 * 16**q, 135) - Fraction(2002 * 4**q, 27) + Fraction(896 * q, 9) + Fraction(4009, 45),
             0: lambda q: Fraction(1210 * 16**q, 27) - Fraction(4235 * 4**q, 54) + Fraction(896 * q, 9) + Fraction(2035, 9)}
    LEAD = {4: 5408 / 135, 0: 1210 / 27}
    HSTEPS = lambda q: 24 * q + 13
    HONES = lambda q, j: 2 * q + j + 2                # (100)^(2q) 01 0000 1^(j+1)

n = 10; j = 0; t = 0
steps = 40                 # exact while known
exact = True
K = None; nm = None        # modular mode: n mod 3^K
log_n = None               # log10 n (float) when n not exact; for deeper levels, log10 log10 n etc.
size_desc = None
hist = []
while True:
    if exact:
        r = n % 6; q = n // 6
        desc = 'n=%d' % n if n < 10**30 else 'n ~ 10^%.6f (%d digits)' % (log10(n) if n < 10**300 else len(str(n)) - 1, len(str(n)))
    else:
        r = {0: 0, 1: 4, 2: 2}[nm % 3]
        desc = 'n = ' + size_desc + '  (n mod 3^%d known)' % K
    print('reset %d: Z-config, %s, j=%d, n mod 6 = %d' % (t, desc, j, r))
    if r == HALTCLASS:
        print('  -> HALTS at reset %d (n in halting class)' % t)
        if exact:
            q = n // 6
            hs = HSTEPS(q)
            print('  halting config after %d more steps; total steps to halting config = %d, +1 halting transition'
                  % (hs, steps + hs))
            print('  ones on tape at halting config = %d' % HONES(q, j))
        break
    A, c, s = RULE[r]
    if exact:
        q = (n - r) // 6
        assert q >= 1 + s
        if steps is not None and q < 10**6:
            tq = TSTEP[r](q); assert tq.denominator == 1
            steps += int(tq)
        else:
            if steps is not None:
                lq0 = log10(q) if q < 10**300 else (len(str(q)) - 1 + log10(int(str(q)[:15]) / 10**14))
                print('   steps from this reset to the next ~ %.4f * 16^q, i.e. 10^(10^%.6f)' % (LEAD[r], lq0 + log10(log10(16))))
            steps = None
        if q < int(EXD / L4):
            n2 = A * 4**(q - s) + c; assert n2 % 3 == 0
            n = n2 // 3
            sd = 'not tracked' if steps is None else (str(steps) if steps < 10**40 else '~10^%.6f (%d digits)' % (len(str(steps)) - 1 + log10(int(str(steps)[:15]) / 10**14), len(str(steps))))
            print('   q=%s -> next n exact (%d digits); exact step count at next reset: %s' % (q if q < 10**30 else '~10^%d' % (len(str(q)) - 1), len(str(n)), sd))
        else:
            # switch to modular with K0 digits: need (q - s) mod 3^(K0) -> 4^(q-s) mod 3^(K0+1)
            K = K0 + 1
            P = pow(4, (q - s) % 3**(K - 1), 3**K)
            v = (A * P + c) % 3**K; assert v % 3 == 0
            nm = (v // 3) % 3**(K - 1); K = K - 1
            # size: log10 n' = (q-s) log10 4 + log10(A/3)
            lq = log10(q) if q < 10**300 else (len(str(q)) - 1 + log10(int(str(q)[:15]) / 10**14))
            size_desc = '10^(10^%.6f)' % (lq + log10(L4))
            loglog = lq + log10(L4)        # log10 log10 n
            print('   q ~ 10^%.6f exact -> next n = (%d*4^(q%s)+%d)/3 ~ %s; switching to 3-adic mode with K=%d'
                  % (lq, A, '-%d' % s if s else '', c, size_desc, K))
            exact = False
            level = 2            # n ~ 10^10^loglog
            steps = None
    else:
        # q = (n - r)/6 mod 3^(K-1); need 4^(q-s) mod 3^K
        inv2 = pow(2, -1, 3**K)
        h = ((nm - r) * inv2) % 3**K; assert h % 3 == 0
        qm = (h // 3) % 3**(K - 1)
        P = pow(4, (qm - s) % 3**(K - 1), 3**K)
        v = (A * P + c) % 3**K; assert v % 3 == 0
        nm = (v // 3) % 3**(K - 1); K -= 1
        level += 1
        size_desc = '10^' * (level - 1) + '(10^%.6f)' % loglog + '  [tower: log10 applied %d times gives %.4f]' % (level, loglog)
        if K < 3:
            print('precision exhausted'); break
    j += 1; t += 1
