import sys
import planner8 as pl
from planner8 import drive
import phases884 as P
pl.set_tm(P.TM)
names=sys.argv[1:] or list(P.PH)
for nm in names:
    st,tg=P.PH[nm]
    try:
        script,_=drive(nm,st,tg,matchers=(),maxev=400,verbose=False)
        print(nm,'OK' if script[-1][0]=='end' else 'FAIL '+str(script[-2:]), [o for o in script][:3])
    except Exception as e:
        print(nm,'EXC',repr(e)[:200])
