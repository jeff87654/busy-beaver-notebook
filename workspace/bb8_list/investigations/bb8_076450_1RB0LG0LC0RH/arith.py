"""Arithmetic of the halting trajectory, done two independent ways.
Rules (see report):  Y(3k+3) ->* Y(4*B(k,5)+9);  Y(3m+13) ->* Y(4*B(m,33)+9);  Y(3k+2) -> halt,
where B(c,b) = g^c(b), g(b) = 4b+5, i.e. 3*B(c,b)+5 = 4^c*(3b+5).
Blank tape ->* Y(4) ->* Y(13) ->* Y(141) = Y(3*46+3) ->* Y(N3), N3 = 4*B(46,5)+9.
"""
from math import log10
L4 = log10(4)

def B(c, b):
    for _ in range(c): b = 4 * b + 5
    return b

def Bm(c, b, m):
    for _ in range(c): b = (4 * b + 5) % m
    return b

N3 = 4 * B(46, 5) + 9
assert N3 == (20 * 4**47 + 7) // 3 and (20 * 4**47 + 7) % 3 == 0
print('N3 =', N3, '(%d digits), N3 mod 3 = %d' % (len(str(N3)), N3 % 3))
assert N3 % 3 == 1
M3 = (N3 - 13) // 3
print('M3 = (N3-13)/3 =', M3, '; M3 mod 27 =', M3 % 27)

# Method 1: closed form N_{i+1} = (104*4^(M+1) + 7)/3 = (416*4^M+7)/3 with M = (N_i-13)/3 ; 3-adic, exponent reduced mod ord(4 mod 3^e) = 3^(e-1)
def next_mod(M_res, e):
    """M known mod 3^e (e>=2): return N' = (104*4^(M+1)+7)/3 mod 3^(e-1) (exact, since 4^M mod 3^e depends on M mod 3^(e-1))."""
    mod = 3**e
    v = (104 * pow(4, (M_res + 1) % 3**(e - 1), mod) + 7) % mod
    assert v % 3 == 0
    return v // 3
# Method 2: N' = 4*B(M,33)+9 with B(M,33) mod 3^e = Bm(M mod 3^e, 33, 3^e)   (g^(3^e) = id mod 3^e)
def next_mod2(M_res, e):
    mod = 3**e
    bm = Bm(M_res % mod, 33 % mod, mod)
    return (4 * bm + 9) % mod

E = 10   # method 2 iterates g up to 3^E times, keep E small
Mres = M3 % 3**E
N_prev_label = 3
names = []
for step in range(4, 12):
    e = E - (step - 4)
    n1 = next_mod(Mres, e)                  # N_step mod 3^(e-1)
    n2 = next_mod2(Mres, e - 1)             # N_step mod 3^(e-1)
    assert n1 % 3**(e - 1) == n2 % 3**(e - 1), (step, n1, n2)
    r = n1 % 3
    print('N%d mod 3 = %d   (N%d mod 81 = %d; both methods agree mod 3^%d)' % (step, r, step, n1 % 81, e - 1))
    if r == 2:
        print('=> Y(N%d) with N%d = 2 mod 3: halts.' % (step, step)); last = step; break
    assert r == 1
    Mres = ((n1 - 13) // 3) % 3**(e - 2)
    # careful: (n1-13)/3 mod 3^(e-2) requires n1 mod 3^(e-1)
print()
# magnitudes
k3 = M3
log_N4 = log10(104 / 3) + M3 * L4                   # log10 N4 (up to ~1e-30 relative)
print('log10 N4 = %.6e' % log_N4)
# N5 = (104*4^M4+7)/3, M4 = (N4-13)/3 : log10 N5 = log10(104/3) + M4*L4 ; log10 log10 N5 = log10(M4*L4) (+ negligible)
# log10(M4) = log10 N4 - log10 3 (N4 huge)
lg_lg_N5 = log_N4 - log10(3) + log10(L4)
print('log10 log10 N5 = %.6e' % lg_lg_N5)
lg_lg_lg_N6 = lg_lg_N5          # log10 log10 N6 = log10 N5 - log10 3 + log10 L4 ; one more log: log10(log10 N5) (+ tiny)
lg4_N6 = log10(lg_lg_N5)
print('log10 log10 log10 N6 = log10 log10 N5 + O(10^-(10^28)) = %.6e ; log^4 N6 = %.6f' % (lg_lg_lg_N6, lg4_N6))
# sigma = (2*N6+5)/3 : same iterated logs to this precision
x = 5 + log10(log10(lg4_N6))
print('sigma: log^4 = %.6f, log^5 = %.6f  => sigma ~ 10^^%.4f' % (lg4_N6, log10(lg4_N6), 5 + log10(log10(lg4_N6))))
