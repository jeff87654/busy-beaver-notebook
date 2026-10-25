import sys
from gen_cyc import *
s,t,pos=ITEMS[sys.argv[1]]
sp=int(sys.argv[2]); dp=int(sys.argv[3])
try:
    tree=mexp.explore(s,t,depth=dp,splits=sp,positive=frozenset(pos))
    print('OK')
except mexp.Fail as e:
    m=str(e); print(m[:300]); print('...'); print(m[-300:])
