"""try_pfxk.py L E : prefix D0f t L (6p+18+E) s y l -> Kgx-shaped pre-ESC target (clean form). L in {14,20}."""
import sys, time, pickle
from common import *
import d0spec, mexp
from d0spec import D0
L=int(sys.argv[1]); E=int(sys.argv[2])
INFO={14:(7,4,[]), 20:(6,5,[4])}     # Kc0, DT, key toks between counter 6 and D(y)
Kc0,DT,ktoks=INFO[L]; Kc=Kc0+E
def tokv(x): return [1]+[0,1]*x
def tokrun(v): return [1, run((0,1),**{v:1})]
T=('B',[1,0,0,1]+[run(TB,t=1)]+list(TB)*DT+[1,1]+[0,1,0,1]+[1,0,1]
    +[run((1,0,1)*6,p=1)]+[1,0,1]*Kc+tokv(7)+tokv(6)+sum([tokv(x) for x in ktoks],[])+tokrun('y')+tokrun('s')+[1,V('l')],[BLANK],'>')
d0spec.PB=6; d0spec.KL=6
S=D0(1,'s',0,'y',18+E,'p',[1]*L)
t0=time.time(); pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
tree=mexp.explore(S,T,splits=0)
print('OK L',L,'E',E,'%.1fs'%(time.time()-t0))
pickle.dump((S,T,tree),open('tree_pk_%d_%d.pkl'%(L,E),'wb'))
