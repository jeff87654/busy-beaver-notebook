"""t0halt.py: (1) stage T0 from the record-family start K(0^35;0;b) for a grid of b including the real class of B
mod 720 (366) and mod 5040 (2526); target [6^(4b+3) 2 0 9 1^(8b+47) | 1 | 1].
(2) the exhaustion stage [6 0 1^z | 1 | R] -> HALT in I reading 0, ones fitted against 2R + 2z + c."""
import sys, collections
import c1lib
mode = sys.argv[1]
if mode == 'T0':
    bs = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(range(0, 61))
    bad = 0
    for b in bs:
        w = c1lib.kstart(b)
        tgt = [6] * (4 * b + 3) + [2, 0, 9] + [1] * (8 * b + 47) + [1, 1]
        line = c1lib.job('reach', c1lib.C1, 2 * 10**11, w, len(w), 'G', tgt); f = line.split()
        ok = f[0] == 'REACHED'; bad += not ok
        print('T0', b, 'OK' if ok else 'BAD', line[:90], flush=True)
    print('T0 bad', bad)
elif mode == 'HALT':
    Rs = [19, 22, 25, 43, 97, 100, 2539, 7579]
    cs = collections.Counter(); bad = 0
    for z in list(range(1, 121)) + [200, 301, 1000]:
        for R in Rs:
            if R > 3000 and z % 7: continue
            f = c1lib.reach([6, 0] + [1] * z + [1, R], [1], maxs=4 * 10**9)
            if f[0] != 'HALT' or f[2] != 'I' or f[3] != '0':
                bad += 1; print('BAD', z, R, f, flush=True); continue
            cs[int(f[4]) - 2 * R - 2 * z] += 1
    print('HALT checks: bad', bad, ' ones - 2R - 2z distribution:', dict(cs))
    for m in (0, 2, 3, 4):
        for z in (30, 31, 32, 100):
            f = c1lib.reach([6] * m + [0] + [1] * z + [1, 43], [1], maxs=10**8)
            print('m', m, 'z', z, f[:5])
