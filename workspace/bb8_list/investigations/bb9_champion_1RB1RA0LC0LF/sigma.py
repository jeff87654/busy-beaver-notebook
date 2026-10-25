import sys
sys.path.insert(0,'.')
from kfam import *
set_shape('D','1')
M='1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH'
for b in (1,3,5,7,9,11,21):
    r=run_next(M,(),0,b,N=10**6)
    s=r[3]
    print('b',b,'steps in R4o',r[1],'ones at halt',s.ones())
# also whole-machine first halt check: simulate blank tape for 3e6 steps (no halt expected)
