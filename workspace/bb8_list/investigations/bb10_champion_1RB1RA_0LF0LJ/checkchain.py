"""Validate a kdtrace output stream: every printed configuration with a == 0 must be followed by the predicted one
(rules.pred with the given R4), and the stream must end in TIMEOUT or a predicted HALT.  Fails loudly.
usage: python checkchain.py TRACEFILE [ch9]"""
import sys
from rules import pred, r4_ch10, r4_ch9
r4 = r4_ch9 if 'ch9' in sys.argv[2:] else r4_ch10
prev = None
n = 0
counts = {}
for line in open(sys.argv[1]):
    f = line.split()
    if not f:
        continue
    if f[0] == 'K':
        step, a, b = int(f[1]), int(f[2]), int(f[3])
        ds = tuple(int(x) for x in f[4].split(',')) if len(f) > 4 else ()
        cur = (ds, a, b)
        if prev is not None and prev[1] == 0:
            p = pred(*prev, r4=r4)
            if p is None or p[0] != 'K' or p[1] != cur:
                print('MISMATCH at step', step, 'from', prev, 'pred', p, 'got', cur)
                sys.exit(1)
            kind = 'R4' if all(d == 0 for d in prev[0]) else ('R2' if prev[0][0] > 0 else 'R3')
            counts[kind] = counts.get(kind, 0) + 1
            n += 1
        prev = cur
    elif f[0] == 'HALT':
        p = pred(*prev, r4=r4) if prev and prev[1] == 0 else None
        print('HALT line', line.strip(), 'last K', prev, 'pred', p)
        sys.exit(0 if p == ('HALT',) else 1)
    elif f[0] == 'TIMEOUT':
        print('OK: %d predicted transitions checked %s, last config a=%d b=%d len(ds)=%d at %s' %
              (n, counts, prev[1], prev[2], len(prev[0]), line.strip()))
        sys.exit(0)
    else:
        print('UNPARSED LINE', line.strip())
        sys.exit(2)
print('stream ended without TIMEOUT/HALT')
sys.exit(2)
