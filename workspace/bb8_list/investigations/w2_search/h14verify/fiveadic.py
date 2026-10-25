"""Exact residues (mod 5^K * small) of the post-round-2 iteration variable X1 and its 5-adic distance to the
fixed point x* of x -> (3x + 2*phi - 87)/5 (phi = residue of every huge U output)."""
import sys
from numth import tau, lam
K = int(sys.argv[1]) if len(sys.argv) > 1 else 40
M = 2**6 * 3**6 * 7**3 * 5**(K + 4)
def inv(a, m): return pow(a, -1, m)
phiM = lambda m: (3 * tau(m) - 8) % m
# T = arrow 37 2 3 is a tall tower of 2s: T = tau mod anything
T = tau(7 * 3 * M)
JJ = (3 * T - 13) % (21 * M); assert JJ % 7 == 0; JJ = (JJ // 7) % (3 * M)
k1 = (4 * JJ - 3) % (3 * M)
ph3 = phiM(9 * M)
u = ((ph3 - 1) // 3) % (3 * M)
nJJ = (34 + JJ * (4 * u + 2)) % (3 * M)
w = (nJJ + 2 * u) % (3 * M)
phi = phiM(9 * M) % (9 * M)
print('k1 mod 8640 =', k1 % 8640, ' phi mod 2520 =', phi % 2520, ' phi mod 5 =', phi % 5)
# round-2 start depth n0 = 7/3 k1 + w + 2/3 U4 + 2/3 U8 - 6  (Per form at stage 24 of drive_r1_lin.log)
num = (7 * k1 + 3 * w + 2 * phi + 2 * phi - 18) % (3 * M)
assert num % 3 == 0; n0 = (num // 3) % M
# PERIODS: m = 2 U11 - 2, r = 8, J = (m - 8)/14 ; n14 = n0 + 2 p0 + 2 u + 2 + (J - 1)(4u + 2), p0 = u (a = U13 = phi)
m = (2 * phi - 2) % (9 * M)
assert (m - 8) % 14 == 0 or True
Jn = (m - 8) % (14 * M)
assert Jn % 14 == 0, Jn % 14
J = (Jn // 14) % M
uu = u % M
n14 = (n0 + 2 * uu + 2 * uu + 2 + (J - 1) * (4 * uu + 2)) % M
a15 = phi % M
X1n = (3 * n14 + 2 * a15 - 11) % M
assert X1n % 5 == 0; X1 = (X1n // 5) % (M // 5)
MM = 5 ** (K + 2)
X1 %= MM
print('n14 mod 2520 =', n14 % 2520, ' n14 mod 25 =', n14 % 25)
xs = (phi - 87 * inv(2, MM)) % MM
print('X1 mod 5 =', X1 % 5, ' x* mod 5 =', xs % 5, ' X1 mod 25 =', X1 % 25)
dlt = (X1 - xs) % MM
v = 0
while dlt % 5 == 0 and v < K: dlt //= 5; v += 1
print('v5(X1 - x*) =', v, '(precision K =', K, ')', ' unit mod 5 =', dlt % 5)
xv1 = (xs % 5 + pow(3, v, 5) * (dlt % 5)) % 5
print('main-branch iterations =', v, '; class of x_(v+1) mod 5 =', xv1)
# ---- decisive-stage chain: D_1 = 3/5 n14 + 2/5 a15 + 2/3 U20 - 418/15 ; D' = (9 D + 10 phi + C_r)/15 for class r = D mod 5
P5 = 5 ** (K + 2)
i3 = pow(3, -1, P5)
n5, a5, ph5 = n14 % P5, a15 % P5, phi % P5
num = (9 * n5 + 6 * a5 - 1254) % P5          # 15 * (3/5 n + 2/5 a - 418/15) - 10*phi  -> handle phi separately
# D1 * 15 = 9 n + 6 a + 10 phi - 418
N15 = (9 * n5 + 6 * a5 + 10 * ph5 - 418) % P5
assert N15 % 5 == 0
D = (N15 // 5) * i3 % (P5 // 5)
C = {0: -415, 1: -319, 2: -388, 3: -412}
mod = P5 // 5
seq = []
for it in range(1, K):
    r = D % 5
    seq.append(r)
    if r == 4: break
    N = (9 * D + 10 * ph5 + C[r]) % mod
    assert N % 5 == 0, ('nondiv', it, r)
    D = (N // 5) * i3 % (mod // 5)
    mod //= 5
print('decisive-stage classes D_i mod 5, i = 1..:', seq)
