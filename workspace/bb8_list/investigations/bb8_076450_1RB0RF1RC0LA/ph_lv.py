import sys
from phases import *
R = {}
R['LVO'] = (Lv([1,0]*3 + run((1,0,1,0),'k')), Lv([1,0]*18 + run((1,0)*8,'k')))
R['LVE'] = (Lv([1,0]*4 + run((1,0,1,0),'k')), BEX([0,1]*2 + run((0,1,0,1),'k'), [1,0]*10))
for nm in (sys.argv[1:] or list(R)):
    s, t = R[nm]
    trydrive(nm, s, t, maxev=3000)
