import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
from explore import ONE6, R, Q, sweepB
def edgeA(cfg):
    q,L,Rr,mode=cfg
    return q=='A' and ((mode=='>' and L==[BLANK] and Rr[0]==0) or (mode=='<' and L==[BLANK]))
pl.STOP_ANY=edgeA
which=sys.argv[1]
c={'Z4':1,'Z0':2,'Z2':3}[which]
L=[1]*(2*c)+mkrun(ONE6,Q)+[1,BLANK]
cfg=('A', L, [1,0,0,0,1]+R, '<')
drive(which, cfg, None, matchers=(sweepB,), maxev=200)
