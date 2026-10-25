"""Probe: start 0^inf (10)^m E> 0^inf in the new machine; print E-edge events and left-edge events."""
import sys
from lit import Sim, ST
M = "1RB1RH_0LC0LF_0RH1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---"
m = int(sys.argv[1]); N = int(sys.argv[2])
s = Sim(M, 1 << 16)
p0 = s.pos
for i, c in enumerate('10' * m):
    s.tape[p0 + i] = int(c)
s.pos = p0 + 2 * m; s.hi = s.pos; s.lo = p0; s.state = ST.index('E')
while s.steps < N:
    k = (ST[s.state], s.tape[s.pos])
    if k in (('C', 0), ('G', 0), ('H', 1)):
        print(s.steps, k, s.show())
    hi = s.hi
    if not s.step(): print('halt', s.steps, s.show(), 'ones', s.ones()); break
    if s.pos > hi and ST[s.state] == 'E':
        print(s.steps, 'E-edge', s.show())
