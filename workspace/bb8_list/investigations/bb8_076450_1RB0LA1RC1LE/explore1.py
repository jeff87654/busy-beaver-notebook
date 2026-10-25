import sys
sys.path.insert(0, '.')
from lit import Sim, ST
M = "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG"
if len(sys.argv) > 2: M = sys.argv[2]
s = Sim(M)
N = int(sys.argv[1])
# print configs when head at left edge (pos == lo) 
last = None
while s.steps < N:
    if s.pos <= s.lo and s.tape[s.pos] == 0:
        print(s.steps, s.show())
    if not s.step():
        print("HALT", s.steps, s.show()); break
