from fam import *
import sys
cfg=family('B',1,1,0)
tgt=family('A',1,0,3)
script,end=drive('B->A',cfg,tgt,maxev=400)
