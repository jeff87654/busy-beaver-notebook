import sys
from tmlit import Sim, ST
from comp import compress
TM = sys.argv[1]
N = int(sys.argv[2])
trig = sys.argv[3]   # e.g. G1
ctx = sys.argv[4] if len(sys.argv) > 4 else ''   # required cells to the left of head, e.g. '00'
s = Sim(TM, size=1 << 22)
tq, tsym = ST.index(trig[0]), int(trig[1])
def rl():
    lo, hi = s.bounds()
    t = s.tape
    L = ''.join(map(str, t[lo:s.pos])); R = ''.join(map(str, t[s.pos+1:hi+1]))
    return '%d %d %s [%s%d] %s' % (s.steps, s.ones(), compress(L,6,2), ST[s.state], t[s.pos], compress(R,6,2))
while s.steps < N:
    if s.state == tq and s.tape[s.pos] == tsym:
        ok = True
        for i, c in enumerate(reversed(ctx)):
            if s.tape[s.pos - 1 - i] != int(c): ok = False; break
        if ok:
            print(rl()[:300], flush=True)
    if not s.step():
        print('HALT', s.steps); break
