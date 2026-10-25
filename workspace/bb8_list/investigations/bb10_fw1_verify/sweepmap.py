"""sweep map W -> outcome.  From [6,6,3,60,401,0,1^w | 2]: the transit D2 is exhausted after one absorption with zero
block W = w + 8.  After the sweep, report the first 'absorption' event [[D1]] D0 D(t) z2 D1^W2 junk, or HALT."""
import sys
from fw import *
from casc import comp
res = []
s = Server(M10, 'Bf,E0', 10 ** 9)
for W in range(int(sys.argv[1]), int(sys.argv[2])):
    w = W - 8
    if w < 1: continue
    L = [6, 6, 3, 60, 401, 0] + [1] * w
    wd, h, q = bword(L, 2)
    started = False; outc = None
    for x in s.job(wd, h, q, 10 ** 9):
        if outc is not None:
            continue
        if x['kind'] == 'HALT':
            outc = 'HALT'; continue
        if x['kind'] != 'EV':
            outc = x['kind']; continue
        it, idx, off = tokpos(x['word'], x['rel'])
        r = it[idx + 1:]
        if not started:
            if len(r) >= 2 and r[0] == 0 and r[1] == 0:
                started = True
            continue
        if it[idx] == 1 and off == 1 and len(r) >= 3 and r[0] == 0 and isinstance(r[1], int) and r[1] > 0 and r[2] == 'z2':
            k = 3; W2 = 0
            while k < len(r) and r[k] == 1:
                W2 += 1; k += 1
            outc = 't=%d W2=%d junk=%s' % (r[1], W2, comp(r[k:]))
    print('W=%d (mod8=%d mod16=%d): %s' % (W, W % 8, W % 16, outc), flush=True)
s.close()
