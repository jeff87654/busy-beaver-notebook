import sys
from tmlit import Sim, ST
from comp import compress
TM = sys.argv[1]
N = int(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else 'left'
s = Sim(TM, size=1 << 22)
prev_at = False
def show():
    lo, hi = s.bounds()
    t = s.tape
    L = ''.join(map(str, t[lo:s.pos])); R = ''.join(map(str, t[s.pos+1:hi+1]))
    return '%d %d %s [%s%d] %s' % (s.steps, s.ones(), compress(L), ST[s.state], t[s.pos], compress(R))
while s.steps < N:
    lo, hi = s.bounds()
    if mode == 'left':
        at = s.pos <= lo
    else:
        at = s.pos >= hi
    if at and not prev_at:
        print(show()[:400])
    prev_at = at
    if not s.step():
        print('HALT', s.steps); break
