import sys
sys.path.insert(0,'.')
from kfam import *
set_shape('D','1')
M='1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH'
N=int(sys.argv[1]) if len(sys.argv)>1 else 10**6
s=Sim(M)
last=0
while s.steps<N:
    r=run_from(s,N-s.steps)
    if r[0]!='K':
        print(r[:3]); break
    print('step %d: %s [+%d]'%(r[1],show(r[2]),r[1]-last)); last=r[1]
