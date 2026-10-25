"""Exact residue of the decisive-stage list length D_i (real run) modulo MB(E), for i = 1..8"""
import sys
from numth import tau
E = int(sys.argv[1]) if len(sys.argv) > 1 else 8
TGT = 2**12 * 3**8 * 5**E * 7**2 * 11 * 13
L = 12
M = TGT * 3**(L + 4) * 5**(L + 4) * 7 * 3        # extra 3,5 precision for the divisions
phiM = lambda m: (3 * tau(m) - 8) % m
T = tau(21 * M); JJ = (3 * T - 13) % (21 * M); assert JJ % 7 == 0; JJ = (JJ // 7) % (3 * M)
k1 = (4 * JJ - 3) % (3 * M)
phi = phiM(27 * M)
u = ((phi - 1) // 3) % (9 * M)
nJJ = (34 + JJ * (4 * u + 2)) % (3 * M); w = (nJJ + 2 * u) % (3 * M)
num = (7 * k1 + 3 * w + 4 * phi - 18) % (3 * M); assert num % 3 == 0; n0 = num // 3 % M
m = (2 * phi - 2) % (14 * M); assert (m - 8) % 14 == 0; J = ((m - 8) // 14) % M
n14 = (n0 + 4 * u + 2 + (J - 1) * (4 * u + 2)) % M
a15 = phi % M
if len(sys.argv) > 4:
    import json; json.dump(dict(n14=int(n14 % TGT), phi=int(phi % TGT)), open(sys.argv[4], 'w'))
N15 = (9 * n14 + 6 * a15 + 10 * phi - 418) % M
assert N15 % 15 == 0
D = (N15 // 15); mod = M // 15
C = {0: -415, 1: -319, 2: -388, 3: -412}
seq = []; ALL = []
STOP = int(sys.argv[2]) if len(sys.argv) > 2 else 8
for it in range(1, 9):
    r = D % 5; seq.append(r); ALL.append(D % TGT)
    if it == STOP or r == 4: break
    N = (9 * D + 10 * phi + C[r]) % mod
    assert N % 15 == 0, ('nondiv', it)
    D = N // 15; mod //= 15
assert mod % TGT == 0
print('classes', seq, 'iteration', len(seq))
print('D mod TGT =', D % TGT, ' D mod 5^E =', D % 5**E, ' D mod 3 =', D % 3)
if len(sys.argv) > 3:
    import json; json.dump([int(x) for x in ALL], open(sys.argv[3], 'w'))
