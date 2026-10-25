import sys
sys.path.insert(0,'.')
from kfam import *
set_shape('D','1')
M=sys.argv[1] if sys.argv[1].count('_')==8 else '1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH'
args=sys.argv[2:] if sys.argv[1].count('_')==8 else sys.argv[1:]
ds=tuple(int(x) for x in args[0].split(',') if x); a=int(args[1]); b=int(args[2])
s=kstart(M,ds,a,b)
print(0,s.show())
n=0
while True:
    if not s.step(): print('HALT',s.show()); break
    n+=1
    print(n,s.show())
    if parse_at(s) is not None: print('K',parse_at(s)); break
    if n>400: break
