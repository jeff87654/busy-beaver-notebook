"""Exact residue chain of C7's run (phase formulas derived in bb9_c7_coq/notes.txt).  python chain.py"""
import idle
from sympy.ntheory.modular import crt
from tower import tower_mod
M5 = 5 ** 22; M2 = 2 ** 12; M3 = 3 ** 8
MOD = M5 * M2 * M3
T = tower_mod(2 * MOD)
rho = (T - 4) // 2 % MOD          # every accumulator R (and B) = rho mod MOD
def d5(x):
    assert x % 5 == 0, x % 5
    return x // 5
n1 = 11
K2 = d5(27 * rho + 3 * n1 + 10); n3 = 12 * rho + K2 + 4
K4 = d5(27 * rho + 3 * n3 + 10); n5 = 12 * rho + K4 + 4
assert n5 % 5 == 3
K6 = d5(27 * rho + 3 * n5 + 44)
n = K6 - 3; L = 3 * n - 4
print('rho mod 5^10 =', rho % 5**10, 'mod 2^10', rho % 2**10, 'mod 3^6', rho % 3**6)
print('n (cascade digits) mod 5^10 =', n % 5**10, 'mod 6 =', n % 6, ' L1 mod 6 =', L % 6)
c = {1: -23, 3: -14, 4: -32, 0: -20}
k = 22 - 3
for i in range(12):
    r = L % 5
    m5 = 5 ** k
    print('step %d: L mod 5^%d (valid) = %d, mod 2 = %d, mod 3 = %d, r = %d' % (i + 1, k, L % m5, L % 2, L % 3, r))
    if r not in c: break
    L = d5(3 * L + c[r]); k -= 1
