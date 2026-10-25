import sys
from phases import *
R = {}
R['BE'] = (BEX([0,1]*4 + run((0,1,0,1),'a'), [1,0]*4 + run((1,0,1,0),'k')),
           ALX([0,1]*2 + run((0,1,0,1),'a'), [0,1]*33 + run((0,1)*8,'k')))
R['AL'] = (ALX([0,1]*4 + run((0,1,0,1),'a'), [0,1]*3 + run((0,1,0,1),'k')),
           BEX([0,1]*2 + run((0,1,0,1),'a'), [1,0]*24 + run((1,0)*8,'k')))
R['AL1'] = (ALX([0,1]*2, [0,1]*3 + run((0,1,0,1),'k')),
           XCX([1,0]*24 + run((1,0)*8,'k')))
names = sys.argv[1:] or list(R)
for nm in names:
    s, t = R[nm]
    trydrive(nm, s, t, log=('-v' in sys.argv))
