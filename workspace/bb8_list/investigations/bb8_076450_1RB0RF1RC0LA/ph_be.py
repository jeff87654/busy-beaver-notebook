import sys
from phases import *
# beX(2a+3, 2k+4) -> alX(2a+1, 8k+31)
start = BEX([0,1]*4 + run((0,1,0,1),'a'), [1,0]*4 + run((1,0,1,0),'k'))
tgt = ALX([0,1]*2 + run((0,1,0,1),'a'), [0,1]*33 + run((0,1)*8,'k'))
script, end = P.drive('BE', norm(start), norm(tgt), matchers=MATCH, maxev=3000, verbose=False)
print(script[-1], len(script), sum(o[1] for o in script if o[0] in ('steps','end')))
print('END', P.show(end)[:300])
