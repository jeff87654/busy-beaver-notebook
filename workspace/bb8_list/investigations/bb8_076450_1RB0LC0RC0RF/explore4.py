from lit import Sim
import sys
s = Sim(size=1<<24)
N = int(sys.argv[1])
prev = None
while s.steps < N:
    if not s.step():
        print('HALT at', s.steps, s.ones()); break
    if s.state == 3 and s.pos >= s.hi and s.tape[s.pos]==0 and s.tape[s.pos-1]==0:
        j = s.pos-2; c=0
        while s.tape[j]==1: c+=1; j-=1
        if c < 10 or s.tape[j-1]==0:
            sh = s.show()
            print(s.steps, sh if len(sh)<400 else sh[:200]+' ... '+sh[-200:], flush=True)
