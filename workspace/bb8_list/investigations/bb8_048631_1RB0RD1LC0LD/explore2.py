import sys
from tmlit import Sim, ST
from comp import compress
TM = sys.argv[1]
N = int(sys.argv[2])
trig = sys.argv[3]  # e.g. D0 : print config whenever this transition is taken
s = Sim(TM, size=1 << 22)
tq, tsym = ST.index(trig[0]), int(trig[1])
cnt = 0
while s.steps < N:
    q, sym = s.state, s.tape[s.pos]
    if q == tq and sym == tsym:
        lo, hi = s.bounds()
        t = s.tape
        L = ''.join(map(str, t[lo:s.pos])); R = ''.join(map(str, t[s.pos+1:hi+1]))
        print(s.steps, s.ones(), compress(L), '[%s%d]' % (ST[q], sym), compress(R))
        cnt += 1
    if not s.step():
        print('HALT', s.steps); break
