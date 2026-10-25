import sys
from phases import *
R = {}
R['BE'] = (BEX([0,1]*4 + run((0,1,0,1),'a'), [1,0]*4 + run((1,0,1,0),'k')),
           ALX([0,1]*2 + run((0,1,0,1),'a'), [0,1]*33 + run((0,1)*8,'k')))
R['AL'] = (ALX([0,1]*4 + run((0,1,0,1),'a'), [0,1]*3 + run((0,1,0,1),'k')),
           BEX([0,1]*2 + run((0,1,0,1),'a'), [1,0]*24 + run((1,0)*8,'k')))
R['AL1'] = (ALX([0,1]*2, [0,1]*3 + run((0,1,0,1),'k')), XCX([1,0]*24 + run((1,0)*8,'k')))
R['XC'] = (XCX([1,0]*4 + run((1,0,1,0),'j')), Lv([1,0]*31 + run((1,0)*8,'j')))
R['LVO'] = (Lv([1,0]*3 + run((1,0,1,0),'k')), Lv([1,0]*18 + run((1,0)*8,'k')))
R['LVE'] = (Lv([1,0]*4 + run((1,0,1,0),'k')), BEX([0,1]*2 + run((0,1,0,1),'k'), [1,0]*10))
for nm in R:
    s, t = R[nm]
    sc, e = P.drive(nm, norm(s), norm(t), matchers=MATCH, maxev=3000, verbose=False)
    fr = [o[1] for o in sc if o[0]=='lemma' and 'TL' in o[1]]
    mx = max([o[2] for o in sc if o[0]=='cross'] + [0])
    print(nm, sc[-1][0], fr, 'max run-cross', mx)
print(sorted(P.LEMMAS)); print(sorted(pext.SWEEPS))
