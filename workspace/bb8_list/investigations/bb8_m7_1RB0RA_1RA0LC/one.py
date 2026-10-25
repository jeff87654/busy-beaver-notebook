from batch import *
import sys
toks=eval(sys.argv[1]); rs=[int(x) for x in sys.argv[2].split(',')]; N=int(sys.argv[3])
res=run([(toks,r) for r in rs],tail='111001',N=N)
from seqx import rl
for t,r,x in res:
    print(rl(t),r,'->',(x[0],rl(x[1]),x[2]) if isinstance(x,tuple) else x)
