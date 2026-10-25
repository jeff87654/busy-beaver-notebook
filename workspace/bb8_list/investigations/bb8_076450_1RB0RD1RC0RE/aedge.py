"""Print configs with state A reading 0 at the left edge (blank to the left), RLE of the right side."""
import sys
from lit import Sim, MAIN, rle
tm = sys.argv[2] if len(sys.argv) > 2 else MAIN
N = int(sys.argv[1])
s = Sim(tm, size=1 << 20)
prev = 0
while s.steps < N:
    lo0 = s.lo
    if not s.step():
        print('HALT at', s.steps, s.show()); break
    if s.pos < lo0 and s.state == 0:
        t = s.tape; hi = s.hi
        while hi > s.pos and t[hi] == 0: hi -= 1
        w = ''.join(map(str, t[s.pos+1:hi+1]))
        print(s.steps, s.steps - prev, len(w), rle(w)[:300]); prev = s.steps
