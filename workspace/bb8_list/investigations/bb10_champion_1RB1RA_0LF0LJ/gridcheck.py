import sys, itertools
from rules import *
M = sys.argv[1] if len(sys.argv) > 1 else CH10
r4 = r4_ch9 if M == CH9 else r4_ch10
bad = tot = unp = 0
unpred = {}
for n in range(0, 5):
    for ds in itertools.product(range(0, 4), repeat=n):
        if ds and ds[-1] == 0:
            continue
        for a in range(0, 3):
            for b in range(0, 10):
                p = pred(ds, a, b, r4)
                r = run_next(M, ds, a, b, N=10 ** 5)
                tot += 1
                if p is None:
                    unp += 1
                    unpred[(ds, a, b)] = r[:3] if r[0] != 'K' else ('K', r[1], r[2])
                    continue
                ok = (r[0] == 'HALT') if p[0] == 'HALT' else (r[0] == 'K' and r[2] == p[1])
                if not ok:
                    bad += 1
                    if bad < 30:
                        print('MISMATCH', ds, a, b, p, r[:3])
print('machine', M, 'tot', tot, 'unpredicted', unp, 'bad', bad)
if '-v' in sys.argv:
    for k, v in sorted(unpred.items()):
        print('UNPRED', k, v)
