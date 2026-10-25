from fam import *
from pipe import *
import sys
K1,K2=int(sys.argv[1]),int(sys.argv[2])
cfg=family('B',K1,K2,0)
print(pl.show(cfg))
tgt=family('A',K1,K2,3)
script,end=drive('B->A',cfg,tgt,matchers=[pipe_matcher()],maxev=400)
