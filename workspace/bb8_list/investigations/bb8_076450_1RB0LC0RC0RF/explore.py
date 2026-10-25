from lit import Sim
import sys
s = Sim()
N = int(sys.argv[1]); every = int(sys.argv[2]) if len(sys.argv)>2 else 1
for i in range(N):
    if not s.step():
        print('HALT at', s.steps, s.ones()); break
    if i % every == 0:
        print(s.steps, s.show())
