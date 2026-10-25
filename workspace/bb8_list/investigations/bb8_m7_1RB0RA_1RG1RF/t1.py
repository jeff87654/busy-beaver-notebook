import sys
sys.path.insert(0,'.')
from cexp import *
import gen_p0 as g
from gen_p0 import R,Z,BLANK
nu=int(sys.argv[1]); lim=int(sys.argv[2]) if len(sys.argv)>2 else 1
st=('C',[0,1]*nu+[1,1,BLANK],[1,0,1,R('t',Z),0,BLANK],'<')
script,c=run('TLPc',st,lim,40)
print(script[-3:]); print(cs(c))
