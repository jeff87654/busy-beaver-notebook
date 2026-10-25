from lit import *
import sys,re,itertools
ev=[]
def rl(tape,p,q):
    s=render(tape,p,q)
    return " ".join(f"{k}^{len(list(g))}" if k in "01" else k for k,g in itertools.groupby(s))
last=[None]
def cb(n,q,p,tape):
    if q==0 and len(ev)<int(sys.argv[2]):
        s=rl(tape,p,q)
        # only print when A sees left part small
        if tape.get(p-1,0)==0 or tape.get(p,0)==0 or True:
            ev.append((n,s))
run(int(sys.argv[1]),cb)
for n,s in ev: print(n,s)
