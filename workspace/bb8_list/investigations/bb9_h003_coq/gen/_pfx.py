from common import *
from shapes import *
import mexp, sys
def tokv(x): return [1]+[0,1]*x
def tokrun(var): return [1, run((0,1),**{var:1})]
# START D0f t 38 (P+15) s y l  -- parked (001)^(P+15); near 1^38
S=('B',[1,0,0,1, run(TB,t=1), 1,1] + [1]*38 + [0,0,1]*15 + [run((0,0,1),P=1)] + [1,1,0]
    + [run((0,1),y=1)] + [1,0,1] + [run((0,1),s=1)] + [1, V('l')], [BLANK],'>')
# TARGET pre-ESC Kt([l;Ds;Dy;2;8;6], D7, 1^P; 1; 2; t+7): near (101)^P
ds=[run((1,0,1),P=1)] + tokv(7)+tokv(6)+tokv(8)+tokv(2) + tokrun('y')+tokrun('s') + [V('l')]
T=('B',[1,0,0,1]+list(TB)*7+[run(TB,t=1),1,1] + [0,1,0,1] + [1] + ds, [BLANK],'>')  # t+? -- try same t run; adjust after
import time; t0=time.time()
pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
try:
    tree=mexp.explore(S,T,splits=6,maxstages=80)
    print('OK %.0fs'%(time.time()-t0))
except Exception as e:
    import traceback; traceback.print_exc()
