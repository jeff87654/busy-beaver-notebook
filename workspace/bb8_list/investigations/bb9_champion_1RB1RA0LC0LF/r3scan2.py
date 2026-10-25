import sys
sys.path.insert(0,'.')
from kfam import *
set_shape('D','1')
M='1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH'
pre=tuple(int(x) for x in sys.argv[1].split(','))
y=int(sys.argv[2]); bs=range(int(sys.argv[3]),int(sys.argv[4])); K=int(sys.argv[5])
for b in bs:
    print('b=%d'%b)
    for k in range(1,K):
        r=run_next(M,pre+(y,)+(0,)*k,0,b)
        print('   k=%d %s'%(k, show(r[2])[1:] if r[0]=='K' else r[:2]))
