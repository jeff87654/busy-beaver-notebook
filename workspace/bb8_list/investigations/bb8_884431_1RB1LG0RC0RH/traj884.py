"""Literal run from the blank tape (mirror machine); every K configuration is compared with the rule-level successor."""
import sys
from common import *
import check_rules as cr   # reuses predict (runs the grid too; ignore its output)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000000
s = Sim(MIR)
prev = None; n = 0; bad = 0; maxb = 0; rebuilds = []
while s.steps < N:
    r = run_from(s, N - s.steps)
    if r[0] != 'K':
        print('stopped', r[:3]); break
    ds, a, bp = r[2]; b = (bp - 1) // 2
    cur = (tuple(ds), a, b)
    if prev is not None:
        p = cr.predict(*prev)
        if prev[0] == () and prev[1] == 1:
            p = cr.predict((), 0, prev[2] + 1)
        if p is None or p[1] != cur:
            bad += 1; print('MISMATCH', prev, cur, p)
    if prev is not None and prev[0] == () and (prev[1] == 0 or prev[1] == 1):
        rebuilds.append((s.steps, prev))
    prev = cur; n += 1; maxb = max(maxb, b)
print('steps', s.steps, 'K configs', n, 'mismatches', bad, 'max b', maxb, 'rebuilds', len(rebuilds), rebuilds[:6])
