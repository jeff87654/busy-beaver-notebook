"""Independent check of the reset classes of R1/R2: purely modular recurrence on n mod 2*3^K starting from
n0 = 10 (no exact phase, no inverse of 2), cross-checked against the exact values of the first resets."""
import sys
sys.set_int_max_str_digits(0)
M = sys.argv[1]; K = int(sys.argv[2]) if len(sys.argv) > 2 else 600
if M == 'R1':
    RULE = {2: (26, 22, 0), 4: (32, 22, 0)}; HALT = 0
else:
    RULE = {4: (26, 4, 0), 0: (110, 4, 1)}; HALT = 2

def step_exact(n):
    r = n % 6; A, c, s = RULE[r]; q = (n - r) // 6
    x = A * 4**(q - s) + c; assert x % 3 == 0
    return x // 3

def step_mod(nm, K):
    """nm = n mod 2*3^K (K>=2) -> n' mod 2*3^(K-1)"""
    mod = 2 * 3**K
    r = nm % 6; A, c, s = RULE[r]
    qm = ((nm - r) % mod) // 6                      # q mod 3^(K-1)
    e = (qm - s) % 3**(K - 1) + 3**(K - 1)          # e = q-s mod 3^(K-1), e >= 1
    P = pow(4, e, mod)                              # = 4^(q-s) mod 2*3^K (both even, same mod 3^K)
    x = (A * P + c) % mod; assert x % 3 == 0
    return x // 3                                   # n' mod 2*3^(K-1)

ex = [10]
for _ in range(3):
    n = ex[-1]
    if n % 6 == HALT: break
    ex.append(step_exact(n))
nm, k, t = 10 % (2 * 3**K), K, 0
while True:
    cls = nm % 6
    chk = ''
    if t < len(ex):
        chk = ' exact n mod 2*3^%d agrees: %s' % (k, ex[t] % (2 * 3**k) == nm)
    print('reset %d: n mod 6 = %d%s' % (t, cls, chk))
    if cls == HALT:
        print('HALT class reached at reset', t); break
    nm = step_mod(nm, k); k -= 1; t += 1
    if k < 2: print('precision exhausted'); break
