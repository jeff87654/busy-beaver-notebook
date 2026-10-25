import sys
from fw import *
n,b,ev,mx,steps=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3],int(sys.argv[4]),int(float(sys.argv[5]))
w,h,q=K(n,b)
import sys
for x in stream(M10,[("n%db%d"%(n,b),w,h,q)],steps,ev,mx):
    print(show(x),flush=True)
sys.exit()
for x in r:
    if x['kind'] in('EV','HALT'):
        it,idx,off=tokpos(x['word'],x['rel'])
        print(x['n'] if 'n' in x else 'HALT',x['step'],x['q'],x['c'],'h',idx,off,'|',fmt(it[:idx]),'[[',fmt(it[idx:idx+1]),']]',fmt(it[idx+1:]))
    else: print(x)
