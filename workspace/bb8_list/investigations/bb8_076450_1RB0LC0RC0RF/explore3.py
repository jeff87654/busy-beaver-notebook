from lit import Sim
import sys
s = Sim(size=1<<22)
N = int(sys.argv[1])
while s.steps < N:
    if not s.step():
        print('HALT at', s.steps, s.ones()); break
    if s.state == 3 and s.pos >= s.hi and s.tape[s.pos]==0 and s.tape[s.pos-1]==0:
        # count trailing ones before pos-1
        j = s.pos-2; c=0
        while s.tape[j]==1: c+=1; j-=1
        if c < 10:
            print(s.steps, s.show()[-300:], flush=True)
