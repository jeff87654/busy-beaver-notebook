import sys
sys.path.insert(0,'.')
from kfam import *
set_shape('D','1')
M='1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH'
def bits(s):
    lo,hi=s.bounds()
    return ''.join(map(str,s.tape[lo:hi+1])), s.pos-lo, 'ABCDEFGHI'[s.state]
ds=tuple(int(x) for x in sys.argv[1].split(',') if x); a=int(sys.argv[2]); b=int(sys.argv[3])
s=kstart(M,ds,a,b)
print(bits(s))
r=run_from(s)
print(r[:3]); 
if r[0]=='K': print(bits(s))
