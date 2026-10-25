from lit import Sim
import sys
s = Sim()
N = int(sys.argv[1])
cnt=0
while s.steps < N:
    if not s.step():
        print('HALT at', s.steps, s.ones()); break
    # D0 at right edge
    if s.state == 3 and s.pos >= s.hi and s.tape[s.pos]==0:
        cnt+=1
        print(s.steps, s.show())
