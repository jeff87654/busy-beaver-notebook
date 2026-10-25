import sys
from sim import *
from j0look import j0
k, w, f, s0, s1 = map(int, sys.argv[1:6])
every = int(sys.argv[6]) if len(sys.argv) > 6 else 1
m = j0(k, w, f)
st0 = m.steps
L0 = m.base  # tape index of word start at J0
while m.steps - st0 < s1:
    t = m.steps - st0
    if t >= s0 and (t - s0) % every == 0:
        s = m.t.translate(TR).decode()
        lo = L0 - 4; hi = L0 + 140
        line = s[lo:m.h] + m.q + s[m.h:hi] if lo <= m.h < hi else s[lo:hi] + ' @%d' % (m.h - L0)
        print('%5d %s' % (t, line))
    if not m.step(): print('HALT', m.q); break
