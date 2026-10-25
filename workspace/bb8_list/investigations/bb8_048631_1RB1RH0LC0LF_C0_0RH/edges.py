"""Print tape at events: head in state E at a new rightmost cell, and at left-edge events (C0/G0)."""
import sys
from lit import Sim, MAIN, ST
s = Sim(MAIN, 1 << 20)
N = int(sys.argv[1])
while s.steps < N:
    k = (ST[s.state], s.tape[s.pos])
    if k in (('C', 0), ('G', 0)) or k == ('A',1) and s.tape[s.pos-1]==1 and False:
        print(s.steps, k, s.show())
    hi = s.hi
    if not s.step(): print('halt', s.steps, s.show()); break
    if s.pos > hi and ST[s.state] == 'E':
        print(s.steps, 'E-edge', s.show())
