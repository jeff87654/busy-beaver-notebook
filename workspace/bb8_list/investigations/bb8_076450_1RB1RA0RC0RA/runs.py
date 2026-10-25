"""Print tape as run-lengths at right-edge expansion events where the run structure (count) changes."""
import sys
from lit import Sim, MAIN, ST
N = int(sys.argv[1]); tm = sys.argv[2] if len(sys.argv) > 2 else MAIN
s = Sim(tm, size=1 << 20)
def desc():
    t = s.tape; lo, hi = s.lo, s.hi
    while lo < hi and t[lo] == 0: lo += 1
    while hi > lo and t[hi] == 0: hi -= 1
    out = []; i = lo
    while i <= hi:
        j = i
        while j <= hi and t[j] == t[i]: j += 1
        n = j - i
        if t[i] == 1: out.append(str(n))
        else: out.append('.' * n if n <= 3 else '0^%d' % n)
        i = j
    return ' '.join(out), s.pos - lo
prevk = None
while s.steps < N:
    lo0, hi0 = s.lo, s.hi
    if not s.step():
        print('HALT at', s.steps); break
    if s.pos > hi0 or s.pos < lo0:
        d, p = desc()
        k = d.count(' ')
        if k != prevk:
            print(s.steps, ST[s.state], 'pos', p, ':', d)
            prevk = k
