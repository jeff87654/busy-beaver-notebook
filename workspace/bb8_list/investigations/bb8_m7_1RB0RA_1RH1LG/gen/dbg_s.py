import sys
from gen_t1 import *
s,t=STAGES[sys.argv[1]]
try:
    tree=mexp.explore(s,t,depth=int(sys.argv[2]),splits=0)
    print('OK')
except mexp.Fail as e:
    m=str(e); print(m[:600])
