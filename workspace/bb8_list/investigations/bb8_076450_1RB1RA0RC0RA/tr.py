import sys
from lit import Sim, MAIN, ST
a, b = int(sys.argv[1]), int(sys.argv[2])
comp = len(sys.argv) > 3
s = Sim(MAIN, size=1 << 16)
while s.steps < b:
    st, sym = s.state, s.tape[s.pos]
    if not s.step(): print('HALT', s.steps); break
    if s.steps >= a:
        print(s.steps, ST[st] + str(sym), s.show(comp=True))
