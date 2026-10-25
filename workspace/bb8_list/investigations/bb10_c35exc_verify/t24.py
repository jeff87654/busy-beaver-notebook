import sys
from lib import ctok
import absim
P = [2, 1, 1, 0, 2, 1, 0, 1]
def go(t, maxev=100000, big=10**12):
    ev = 0
    hist = []
    try:
        while ev < maxev:
            t2, r = absim.step(t)
            ev += 1
            if r not in ('R1', 'R2'):
                hist.append((ev, r, ctok([v if v < 1000 else 'H%d' % (v % 3) for v in t2])))
            t = t2
            if max(t) > big:
                return 'BIG', ev, t, hist
    except absim.Unknown as e:
        return 'UNKNOWN ' + str(e), ev, t, hist
    return 'MAXEV', ev, t, hist
for (q, A, n) in [(1, 3, 1), (1, 6, 1), (1, 9, 1), (1, 3, 2), (1, 6, 2), (2, 6, 1), (2, 3, 3)]:
    t = P + [6 * q - 1, 3] + [1] * (6 * q) + [A] + [1] * n + [0, 6]
    res, ev, tf, hist = go(t)
    print('q=%d A=%d n=%d ->' % (q, A, n), res, 'events', ev)
    for h in hist[:40]: print('    ', h)
    print('   final', ctok([v if v < 1000 else 'H%d' % (v % 3) for v in tf]))
