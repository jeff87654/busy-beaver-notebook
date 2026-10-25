import sys
import planner9 as pl
from planner9 import mkrun, V, BLANK, drive, show
ONE=(1,)
Iv={'i':1}
class Found(Exception): pass
def md(cfg):
    q,L,R,mode=cfg
    if q=='D' and L==[BLANK] and ((mode=='<') or (mode=='>' and R[0]==0)):
        raise Found(cfg)
md.anytime=True
s0=int(sys.argv[1])
start=('A',[1]*s0+mkrun((0,1,1),Iv)+[BLANK],[BLANK],'>')
try:
    drive('R4end s=%d'%s0,start,None,matchers=(md,),maxev=300,verbose=True,stop_at=None)
except Found as f:
    print('FOUND',show(f.args[0]))
