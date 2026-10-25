"""sweep map: from [6,6,3,60,T,0,1^w | A] (A even small, T large) print the event sequence after the first
transit exhaustion, compressed: one line per E0 event whose right part changed shape.   sweep.py A w1,w2,.. [NEV]"""
import sys, re
from fw import *
from casc import comp
A = int(sys.argv[1])
nev = int(sys.argv[3]) if len(sys.argv) > 3 else 30
for w in [int(x) for x in sys.argv[2].split(',')]:
    T = 401
    L = [6, 6, 3, 60, T, 0] + [1] * w
    wd, h, q = bword(L, A)
    s = Server(M10, 'Bf,E0', 10 ** 9)
    started = False; k = 0; out = []
    for x in s.job(wd, h, q, 10 ** 10):
        if x['kind'] in ('EV', 'HALT'):
            it, idx, off = tokpos(x['word'], x['rel'])
            r = it[idx + 1:]
            if not started:
                if len(r) >= 2 and r[0] == 0 and r[1] == 0:
                    started = True
                else:
                    continue
            # count pairs right boundary: number of (1,0) pairs left of idx
            j = idx - 1; pr = 0
            while j >= 1 and it[j] == 0 and it[j - 1] == 1:
                pr += 1; j -= 2
            out.append('%s %d %s pairs<-%d [[%s]] %s' % (x.get('n', 'HALT'), x['step'], x['q'] + str(x['c']), pr, fmt(it[idx:idx + 1]), comp(r)))
            k += 1
            if x['kind'] == 'HALT' or k >= nev:
                break
        else:
            out.append(str(x['kind'])); break
    s.close()
    print('=== A=%d w=%d W=%d' % (A, w, w + 4 + 2 * A))
    for o in out:
        print('  ', o[:300])
