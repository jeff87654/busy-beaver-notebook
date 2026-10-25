import sys
from tmlit import Sim, ST
from comp import compress
TM = sys.argv[1]
a, b, every = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
s = Sim(TM, size=1 << 22)
def rl():
    lo, hi = s.bounds()
    t = s.tape
    L = ''.join(map(str, t[lo:s.pos])); R = ''.join(map(str, t[s.pos+1:hi+1]))
    return '%d %d %s [%s%d] %s' % (s.steps, s.ones(), compress(L,6,2), ST[s.state], t[s.pos], compress(R,6,2))
while s.steps < b:
    if s.steps >= a and (s.steps - a) % every == 0:
        print(rl()[:300], flush=True)
    if not s.step():
        print('HALT', s.steps); break
