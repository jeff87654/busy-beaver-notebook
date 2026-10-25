"""R2/R3 checks on real-run-shaped lists: Kd (0^k, v, tail) 0 b for depths k up to KMAX, b = 2k..2k+12,
tails taken from the rebuilt list L(b) = [1|3, (0,0,3)^m, 0,0,2].  Also R2 with large digits."""
import sys
from rules import *
M = sys.argv[1] if len(sys.argv) > 1 and '_' in sys.argv[1] else CH10
KMAX = 24
bad = tot = 0
tails = [(), (0, 0, 3), (0, 0, 2), (0, 0, 3, 0, 0, 2), (0, 0, 3, 0, 0, 3, 0, 0, 2)]
for k in range(1, KMAX + 1):
    for v in (1, 2, 3):
        for tail in tails:
            ds = (0,) * k + (v,) + tail
            for b in range(2 * k, 2 * k + 13):
                p = pred(ds, 0, b)
                r = run_next(M, ds, 0, b, N=10 ** 6)
                tot += 1
                if not (r[0] == 'K' and p[0] == 'K' and r[2] == p[1]):
                    bad += 1
                    print('MISMATCH', ds, b, p, r[:3])
for v in (5, 20, 91, 300):
    for b in (0, 1, 7, 50, 500):
        ds = (v, 1, 3, 2, 0, 0, 3, 0, 0, 2)
        p = pred(ds, 0, b)
        r = run_next(M, ds, 0, b, N=10 ** 6)
        tot += 1
        if not (r[0] == 'K' and r[2] == p[1]):
            bad += 1
            print('MISMATCH', ds, b, p, r[:3])
print('deep R2/R3 checks:', tot, 'mismatches:', bad)
