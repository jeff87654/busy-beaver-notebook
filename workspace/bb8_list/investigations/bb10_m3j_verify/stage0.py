"""Literal B-form trace (specials only) from the record end [1^n | 6b+4] for M3J.  stage0.py n b MAXSTEPS"""
import sys
from fw import *
from btrace import classify
n, b = int(sys.argv[1]), int(sys.argv[2])
L, A = [1] * n, 6 * b + 4
srv = Server(M10, 'Bf,E0', 10 ** 9)
tot = 0; prev = None; cnt = {'R1': 0, 'R2': 0}
for it in range(int(sys.argv[4]) if len(sys.argv) > 4 else 200000):
    w, h, q = bword(L, A)
    r = srv.job(w, h, q, int(float(sys.argv[3])))
    x = r[-1]; ne = sum(1 for y in r if y['kind'] == 'EV')
    if x['kind'] != 'BF':
        print('END', x['kind'], tot + (x.get('step') or 0), show(x)[:300]); break
    tot += x['step']
    p = bparse(x['word'], x['rel'])
    c = classify((L, A), p)
    if c:
        cnt[c] += 1
    else:
        print('%d SPECIAL(%dE0) after %s: [%s | %d] -> [%s | %d]' % (tot, ne, cnt, fmt(L)[:120], A, fmt(p[0])[:160], p[1]), flush=True)
        cnt = {'R1': 0, 'R2': 0}
    L, A = p
    if max(L + [A]) > 3000:
        print('BIG at', tot, '[%s | %d]' % (fmt(L)[:200], A)); break
srv.close()
