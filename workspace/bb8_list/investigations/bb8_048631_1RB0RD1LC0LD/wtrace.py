import sys
from msim import *
TM = "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
z, y, x = map(int, sys.argv[1:4])
maxsteps = int(sys.argv[4]); every = int(sys.argv[5])
m = from_blocks(TM, [('010', z), ('000', 1), ('111', 1), ('001', y), ('000', 1), ('011', 1), ('111', 1), ('100', x)], 'E', 'R', [('100', 2), ('110', 1)])
n = 0
try:
    while n < maxsteps:
        if n % every == 0: print(n, m.steps, m.show())
        m.step(); n += 1
except Halt as h:
    print('HALT', h, m.show())
