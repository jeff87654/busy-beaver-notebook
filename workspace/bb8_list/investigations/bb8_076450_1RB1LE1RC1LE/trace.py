import sys
from lit import Sim, MAIN
a, b = int(sys.argv[1]), int(sys.argv[2])
n = int(sys.argv[3])
s = Sim(MAIN, size=4096)
# place E(a,b) : 0^inf E>0 1 (10)^a (01)^b 1^c
c = int(sys.argv[4]) if len(sys.argv) > 4 else 0
w = [1] + [1, 0]*a + [0, 1]*b + [1]*c
p = s.pos
for i, x in enumerate(w): s.tape[p + 1 + i] = x
s.hi = p + len(w)
s.state = 4
for i in range(n):
    print(s.steps, s.show(comp=False))
    if not s.step(): print('HALT'); break
print(s.steps, s.show(comp=False))
