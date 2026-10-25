import sys
from sim import *
from j0look import j0
k, w, f, nmax = map(int, sys.argv[1:5])
qs = sys.argv[5] if len(sys.argv) > 5 else 'KLMN'
m = j0(k, w, f)
st0 = m.steps
n = 0
prevq = ''
while n < nmax:
    q = m.q
    if q in qs and prevq not in qs:
        wd, rel, a = m.word()
        print('%7d %s r%d off%d  %s [%s] %s' % (m.steps-st0, q, m.t[m.h], a, wd[:rel], q, wd[rel:rel+60]))
        n += 1
    prevq = q
    if not m.step(): print('HALT', m.q, m.steps - st0); break
