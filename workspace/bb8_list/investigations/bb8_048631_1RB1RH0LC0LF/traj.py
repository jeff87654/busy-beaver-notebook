# k_{i+1} = (87*9^{k_i} + 1)/16 ; reset i halts if k_i even (n after k_i digits from 2 is even -> m even)
from math import log10
k1 = 49
k2 = (87 * 9**k1 + 1)
assert k2 % 16 == 0
k2 //= 16
print('k1 =', k1, 'odd' if k1 % 2 else 'even')
print('k2 =', k2, 'odd' if k2 % 2 else 'even', 'mod 64 =', k2 % 64, 'log10 = %.4f' % log10(k2))
# k3 mod 2^J
J = 200
M = 2 ** (J + 4)
x = (87 * pow(9, k2, M) + 1) % M
assert x % 16 == 0
k3 = x // 16  # mod 2^J
print('k3 mod 2^8 =', k3 % 256, 'parity', k3 % 2)
# k4 mod 2^(J-?) : 9 has order 2^(e-3) mod 2^e for e>=3, so 9^k mod 2^(J2+4) needs k mod 2^(J2+1)
J2 = J - 1
M2 = 2 ** (J2 + 4)
x = (87 * pow(9, k3 % 2 ** (J2 + 1), M2) + 1) % M2
assert x % 16 == 0
k4 = x // 16
print('k4 mod 2^8 =', k4 % 256, 'parity', k4 % 2)
