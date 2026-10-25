import idle
"""cmpm8.py H003FILE M8FILE: for every K run by both machines from the same exit Top(K): same outcome?  same CL sequence
up to depth offsets?  Reports the multiset of (depth offset per CL) and of (ones difference)."""
import sys, re
from collections import Counter
def load(fn):
    d = {}
    for line in open(fn):
        m = re.search(r' K=(\d+) .*?\| (HALT \S+|MAXS|NONE)[^|]*?(?:ones=(\d+))?[^|]*\| bad=(\d+) \| ncl=(\d+) .*?\| (.*)$', line.strip())
        if m:
            o = re.search(r' ones=(\d+)', line); d[int(m.group(1))] = (m.group(2), int(o.group(1)) if o else -1, int(m.group(4)), m.group(6).split())
    return d
A, B = load(sys.argv[1]), load(sys.argv[2])
offs, dones, bad = Counter(), Counter(), 0
for K in sorted(set(A) & set(B)):
    a, b = A[K], B[K]
    ok = a[0] == b[0] and len(a[3]) == len(b[3])
    o = []
    if ok:
        for x, y in zip(a[3], b[3]):
            if x == 'CNT' or y == 'CNT':
                ok &= x == y; continue
            (X1, k1), (X2, k2) = map(int, x.split('/')), map(int, y.split('/'))
            if X1 != X2 and not (X1 >= 500 and X2 >= 500): ok = False
            o.append(k1 - k2)
    if not ok:
        bad += 1; print('DIFF K=%d\n  h003 %s %s\n  M8   %s %s' % (K, a[0], ' '.join(a[3])[:300], b[0], ' '.join(b[3])[:300])); continue
    offs[tuple(sorted(set(o)))] += 1; dones[a[1] - b[1]] += 1
print('compared', len(set(A) & set(B)), 'structurally different', bad)
print('depth-offset sets (h003 - M8):', dict(offs))
print('ones difference (h003 - M8):', dict(dones))
