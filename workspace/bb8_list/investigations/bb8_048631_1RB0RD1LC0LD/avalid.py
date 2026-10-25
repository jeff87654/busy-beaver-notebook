import sys
from msim import *
import asim
TM = "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
def mk():
    return from_blocks(TM, [('010', 8), ('000', 1), ('111', 1), ('001', 30), ('000', 1), ('011', 1), ('111', 1), ('100', 2)], 'E', 'R', [('100', 1), ('110', 1)])
def ev(m):
    return m.q == 'E' and m.d == 'R' and len(m.R) == 2 and m.R[-1] == [(1,0,0), 1] and m.R[0] == [(1,1,0), 1]
N = int(sys.argv[1])
m = mk(); evs1 = []
while m.steps < N:
    m.step()
    if ev(m): evs1.append((m.steps, m.show()))
m2 = mk(); a = asim.ASim(m2); evs2 = []
while m2.steps < N:
    a.step()
    if ev(m2): evs2.append((m2.steps, m2.show()))
print(len(evs1), len(evs2))
for x, y in zip(evs1, evs2):
    print(x[0] == y[0], x[1] == y[1], x[0], x[1][:150])
    if x != y: print('   ', y)
