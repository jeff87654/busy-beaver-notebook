from rules import *
import sys
res = {}
for T in range(9, 50, 4):
    for d in range(-4, 4):
        A = (T - 5) // 2 + d
        if A < 0: continue
        L = [6, 6, 20, T, 0, 1, 1, 1]
        exp = p_ED0(L, A)
        k, L2, A2, st = lit(L, A)
        good = (k == 'B' and (L2, A2) == exp)
        V = A + 1 - (T - 5) // 2
        res.setdefault(V, []).append((T, A, good, k))
for V in sorted(res):
    print('V=%d' % V, ' '.join('T%d:A%d:%s' % (T, A, 'ok' if g else k) for T, A, g, k in res[V]))
