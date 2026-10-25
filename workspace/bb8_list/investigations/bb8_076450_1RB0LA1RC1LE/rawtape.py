import sys
from lit import Sim
M = sys.argv[1]; N = int(sys.argv[2]); maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 120
s = Sim(M, size=1<<16)
while s.steps < N:
    if s.state == 4 and s.pos <= s.lo and s.tape[s.pos] == 0:
        t = s.tape; hi = s.hi
        while hi > s.pos and t[hi] == 0: hi -= 1
        R = ''.join(map(str, t[s.pos+1:hi+1]))
        print(s.steps, len(R), R[:maxlen] + ('...' + R[-40:] if len(R) > maxlen else ''))
    if not s.step():
        print("HALT", s.steps); break
