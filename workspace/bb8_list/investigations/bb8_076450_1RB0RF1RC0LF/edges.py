import sys
from lit import Sim, MAIN
tm = sys.argv[3] if len(sys.argv) > 3 else MAIN
N = int(sys.argv[1]); side = sys.argv[2]
s = Sim(tm)
while s.steps < N:
    lo0, hi0 = s.lo, s.hi
    if not s.step():
        print('HALT at', s.steps, s.show()); break
    if side == 'L' and s.pos < lo0:
        print(s.steps, s.show())
    if side == 'R' and s.pos > hi0:
        print(s.steps, s.show())
