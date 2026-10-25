import idle, sys, hashlib
import numpy as np
from resid import Eng
M = int(sys.argv[1]); J = int(sys.argv[2])
e = Eng(M, J)
print('bad', e.bad[:5], 'tails max', max(t for t, p in e.lev), 'periods', sorted(set(p for t, p in e.lev)))
h = [hashlib.md5(e.arr[j].tobytes()).hexdigest()[:8] for j in range(J + 1)]
# periodicity of the map sequence Phi_j for large j
for P in range(1, 300):
    if all(h[j] == h[j - P] for j in range(J // 2, J + 1)): print('Phi_j periodic in j from', J // 2, 'with period', P); break
# F(n) = A_E([(1,0)^n], 1): composite = Phi_{2n-1} o Phi_{2n-3} o ... o Phi_1 (1)
x = 1; F = []
for n in range(1, J // 2 + 1):
    pass
# direct: for list (1,0)^n positions j = 1,3,...,2n-1 applied in order j=1 first
F = []
for n in range(1, J // 2 + 1):
    x = 1
    for j in range(1, 2 * n, 2): x = int(e.arr[j][x])
    F.append(x)
print('F(n) n=1..20:', F[:20])
print('F(425) mod', M, '=', F[424] if len(F) >= 425 else None)
