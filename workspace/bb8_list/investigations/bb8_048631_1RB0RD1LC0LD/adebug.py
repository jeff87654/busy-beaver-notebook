import sys
from msim import *
import asim
TM = "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
m = from_blocks(TM, [('010', 8), ('000', 1), ('111', 1), ('001', 30), ('000', 1), ('011', 1), ('111', 1), ('100', 1)], 'E', 'R', [('100', 2), ('110', 1)])
a = asim.ASim(m)
last = 0
while a.nmacro < 200000:
    before = m.show()
    a.step()
    if a.accel != last:
        last = a.accel
        print('ACCEL at', a.nmacro)
        print('  before', before[:250])
        print('  after ', m.show()[:250])
        if a.accel > 40: break
