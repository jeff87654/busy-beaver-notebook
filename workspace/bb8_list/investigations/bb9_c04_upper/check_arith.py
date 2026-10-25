# check_arith.py : small-parameter checks of the arrow / U / FGH facts used in upper.txt (exact big integers, or log2 towers).
import math, sys
sys.set_int_max_str_digits(0) if hasattr(sys, 'set_int_max_str_digits') else None
def G(m, n, capbits=70000):
    """2 ^^m n (m>=0): G(0,n)=2n, G(m+1,1)=2, G(m+1,n+1)=G(m,G(m+1,n)); None if it exceeds 2^capbits"""
    if n is None: return None
    if m == 0: return 2 * n
    if m == 1: return (1 << n) if n <= capbits else None
    y = 2
    for _ in range(n - 1):
        y = G(m - 1, y, capbits)
        if y is None: return None
    return y
def U(j, x):
    if j == 0: return (1 << (2 * x + 3)) - 2
    y = 0
    for _ in range(2 * x + 2): y = U(j - 1, y)
    return y
phi = lambda x: 2 * x + 4
ok = True
# L1  (G_m)^n(2) = G_{m+1}(n+1)
for m in range(0, 3):
    for n in range(0, 4):
        y = 2
        for _ in range(n): y = G(m, y) if y is not None else None
        g = G(m + 1, n + 1)
        if y is not None and g is not None: ok &= (y == g); print('L1 m=%d n=%d' % (m, n), y == g)
# L2  phi(U_d^v(0)) = G_{d+2}(v+2)
for d, v in ((0, 1), (0, 2), (0, 3), (1, 1)):
    x = 0
    for _ in range(v): x = U(d, x)
    g = G(d + 2, v + 2); ok &= phi(x) == g; print('L2 d=%d v=%d' % (d, v), phi(x) == g)
# L3  (G_m)^n(y) <= G_{m+1}(n+y),  y >= 2  (and >= G_{m+1}(n+1))
for m in range(0, 2):
    for n in range(0, 4):
        for y in range(2, 6):
            a = y
            for _ in range(n):
                a = G(m, a) if a is not None else None
            b = G(m + 1, n + y); c = G(m + 1, n + 1)
            if a is not None and b is not None: ok &= c <= a <= b; print('L3 m=%d n=%d y=%d' % (m, n, y), c <= a <= b)
# F1/F2  G_{k-1}(n) <= f_k(n) <= G_{k-1}(4n)  for k=2 (all n<=30) and k=3, n=1,2 exactly; f_3(3) via log2
f1 = lambda n: 2 * n
f2 = lambda n: n * (1 << n)
for n in range(2, 31): ok &= (1 << n) <= f2(n) <= (1 << (4 * n))
print('F k=2 n=2..30', ok)
f3_2 = f2(f2(2)); ok &= G(2, 2) <= f3_2 and f3_2.bit_length() <= 65536; print('F k=3 n=2: f_3(2) =', f3_2, '>= G_2(2)=4, and < 2^65536 = G_2(5) <= G_2(8)')
# f_3(3) = f2(f2(f2(3))) : log2 f_3(3) = log2(a) + a with a = f2(f2(3)) = f2(24); G_2(3)=16 <= f_3(3) <= G_2(12)
a = f2(f2(3)); lg = a + a.bit_length(); print('F k=3 n=3: log2 f_3(3) ~', lg, '(G_2(3)=16 below; G_2(12) has log2 = G_2(11), a tower of 11) ->', lg > 4)
# endgame arithmetic: integrality of z and C, C = 0 mod 3, for every K in its residue class (K mod 15 covers all cases)
cp = {0: 30, 1: 33, 2: 21, 3: 34, 4: 37}
for K in range(60, 60 + 15 * 20):
    r = K % 5; ok &= (3 * K - cp[r]) % 5 == 0
    for RE in (0, 1, 2):
        if r == 0: C = 6 * RE + (3 * K + 45) // 5; ok &= (3 * K + 45) % 5 == 0 and C % 3 == 0
        if r == 2: ok &= (3 * K + 9) % 5 == 0 and ((3 * K + 9) // 5) % 3 == 0
        if r == 3: ok &= (3 * K - 9) % 5 == 0 and ((3 * K - 9) // 5) % 3 == 0
        if r == 4:
            ok &= (3 * K - 12) % 5 == 0 and ((3 * K - 12) // 5) % 3 == 0
            for Rp in (0, 1, 2): ok &= (6 * Rp + 6 * RE + 15) % 3 == 0
        if r == 1: z = (3 * K - 33) // 5; ok &= (z + 7) % 3 == 1      # X = z+7 is a digit token
print('endgame residue identities (K = 60..359, R residues 0..2):', ok)
print('ALL OK' if ok else 'FAILURE')
