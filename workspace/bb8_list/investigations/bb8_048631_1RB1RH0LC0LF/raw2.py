import sys
from lit import Sim, MAIN, ST
ts = sorted(int(x) for x in sys.argv[1].split(','))
s = Sim(MAIN, 1 << 22)
base = s.pos
for T in ts:
    while s.steps < T:
        if not s.step(): print('HALT'); break
    t = s.tape
    lo = min(s.lo, base - 400)
    L = ''.join(map(str, t[s.lo:s.pos])); R = ''.join(map(str, t[s.pos+1:s.hi+1]))
    print(s.steps, 'lo-off', s.lo - base, 'pos-off', s.pos - base)
    print('   ', L, '[%s%d]' % (ST[s.state], t[s.pos]), R)
