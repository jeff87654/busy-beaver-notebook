"""try_prefix.py KEY E : explore the entry prefix D0f(key+1) -> pre-ESC Kt(ctx, 6, D7, 1^K), parked P=6p+E+PBASE.
 pre-ESC ctx (nearest-first after D7): counter 6, then key-fixed tokens, then D(y), D(s), then far l.  K = P - OFF(key)."""
import sys, time, pickle
from common import *
import d0spec
from d0spec import *
import mexp
KEY=int(sys.argv[1]); E=int(sys.argv[2]); d0spec.PB=6; d0spec.KL=6
L=KEY+1
PBASE=18
# fixed key tokens (nearest-first, between counter 6 and D(y)) and near offset OFF and tail delta DT
KEYINFO={37:([8,2],15,7), 43:([10,6],17,7), 49:([4,12,4],18,8)}
ktoks,OFF,DT=KEYINFO[KEY]
def tokv(x): return [1]+[0,1]*x
def tokrun(var): return [1, run((0,1),**{var:1})]
# START: D0f with near 1^L (L literal), parked (001)^(6p+E+PBASE), acc (01)^s via d0spec.D0
S=D0(1,'s',0,'y',E+PBASE,'p',[1]*L)
# TARGET: Kt(...; 1; 2; t+DT): near (101)^K, K=6p+E+PBASE-OFF ; then D7, counter6, ktoks, Dy, Ds, l
K_const=E+PBASE-OFF
near=[run((1,0,1),p=6)]+[1,0,1]*K_const if K_const>=0 else None
ds=near + tokv(7) + tokv(6) + sum([tokv(x) for x in ktoks],[]) + tokrun('y')+tokrun('s') + [V('l')]
# Kt wrapper with t+DT tail blocks: tailpart with (TB)^DT prepended to the run
T=('B',[1,0,0,1]+list(TB)*DT+[run(TB,t=1),1,1] + [0,1,0,1] + [1] + ds, [BLANK],'>')
print('L',L,'K_const',K_const); print('S',pl.show(S)[:110]); print('T',pl.show(T)[:110])
t0=time.time()
pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
tree=mexp.explore(S,T,splits=0)
print('OK %.1fs'%(time.time()-t0))
pickle.dump((S,T,tree),open('tree_pfx_%d_%d.pkl'%(KEY,E),'wb'))
