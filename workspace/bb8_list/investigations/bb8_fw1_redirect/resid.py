"""resid.py: residue engine for the F1 K-rules (D a->3a+3; Bk refill 3a+3-2k, tail 2^(k-1), a:=2; E = empty list).
A_E(ds, a) = Phi_{n-1}^{d_1} o ... o Phi_0^{d_n} (a), Phi_0(a) = 3a+3, Phi_j(a) = Phi_{j-1}^{3a+3-2j}(c_j), c_j = g_{j-1}(2),
g_m(a) = Phi_{m-1}^2(g_{m-1}(a)), g_0(a) = a.  Values are residues mod M (plus exact ints while small).
Phi_j is stored as (orbit of c_j under Phi_{j-1}, tail, period); it needs the iteration count mod the period -> period | M required."""
import idle, sys
import numpy as np
class Eng:
    def __init__(s, M, J):
        s.M = M; s.lev = []          # lev[j] = None for j=0, else (orbit array, tail, period)
        s.arr = [None] * (J + 1)      # full map arrays Phi_j on Z_M
        a = np.arange(M, dtype=np.int64); s.arr[0] = (3 * a + 3) % M
        s.bad = []
        for j in range(1, J + 1):
            c = s.g(j - 1, 2)          # residue
            f = s.arr[j - 1]; seen = {}; orb = []; x = c
            while x not in seen: seen[x] = len(orb); orb.append(x); x = int(f[x])
            t = seen[x]; p = len(orb) - t
            if M % p: s.bad.append((j, p))
            orb = np.array(orb, dtype=np.int64)
            r = (3 * a + 3 - 2 * j)      # iteration count residue mod M; valid index if p | M and true r >= t
            idx = t + ((r - t) % p)
            s.arr[j] = orb[idx]; s.lev.append((t, p))
    def g(s, m, a):
        x = a % s.M
        for i in range(1, m + 1):
            f = s.arr[i - 1]; x = int(f[int(f[x])])
        return x
    def AE(s, ds, a):
        x = a % s.M; n = len(ds)
        for i in range(n - 1, -1, -1):
            j = n - 1 - i
            for _ in range(ds[i]): x = int(s.arr[j][x])
        return x
if __name__ == '__main__':
    M = int(sys.argv[1]); J = int(sys.argv[2])
    e = Eng(M, J)
    print('M', M, 'levels', J, 'bad periods', e.bad[:10])
    print('tails/periods first 12:', e.lev[:12])
    print('check [1,0;1] ->', e.AE([1, 0], 1), '(literal 282 ->', 282 % M, ')')
