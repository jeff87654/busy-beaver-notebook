from lit import *
import sys
ev=[]
st={'lo':0,'hi':0}
def cb(n,q,p,tape):
    if q==0 and len(ev)<60:
        ev.append((n,render(tape,p,q)))
run(int(sys.argv[1]),cb)
for e in ev: print(e[0],e[1][:200])
