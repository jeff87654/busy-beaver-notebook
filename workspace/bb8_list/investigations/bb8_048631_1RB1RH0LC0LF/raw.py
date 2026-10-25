import sys
from lit import Sim, MAIN, ST
a, b = int(sys.argv[1]), int(sys.argv[2]); st = sys.argv[3] if len(sys.argv) > 3 else 'E'
lastk = int(sys.argv[4]) if len(sys.argv) > 4 else 80
s = Sim(MAIN, 1 << 22)
while s.steps < b:
    hi0 = s.hi
    if not s.step():
        print('HALT', s.steps); break
    if s.steps >= a and s.pos > hi0 and ST[s.state] == st:
        t = s.tape
        L = ''.join(map(str, t[s.lo:s.pos]))
        print(s.steps, len(L), '...' + L[-lastk:], '[%s]' % st)
