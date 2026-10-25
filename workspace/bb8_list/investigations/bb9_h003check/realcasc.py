import idle
"""realcasc.py: the real exit exhaustion's computable prefix: L0 = 3K4-2 (K4 from orbit.py), M8 sub-step map with stops."""
from orbit import Rstar, RULE
P = 5 ** 60; Rs = Rstar(P); K = (12 * Rs + 27) % P; mod = P
while K % 5 in RULE:
    a, c = RULE[K % 5]; K = (a * K + 60 * Rs + c) // 5 % (mod // 5); mod //= 5
L = (3 * K - 2) % mod
print('K4 = %d mod 5^%d' % (K % 5 ** 12, 12), ' L0 mod 5^12 =', L % 5 ** 12)
ex, sub, out = 1, [], []
for step in range(40):
    r = L % 5
    if r == 0:
        out.append('exh%d: %s stop' % (ex, ''.join(map(str, sub)))); sub = []; ex += 1
        L = (3 * L - 100) * pow(1, 1) // 5; mod //= 5; L %= mod; continue
    c = {1: 32, 2: -46, 3: -64, 4: -52}[r]
    sub.append(r); L = (3 * L + c) // 5 % (mod // 5); mod //= 5
print(' | '.join(out), '| current', ''.join(map(str, sub)), '(precision left 5^%d)' % len(str(mod)) if False else '')
