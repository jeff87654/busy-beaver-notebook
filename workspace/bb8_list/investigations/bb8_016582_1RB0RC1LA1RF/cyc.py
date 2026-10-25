from lit import parse
import sys, threading, os
threading.Timer(80, lambda: os._exit(3)).start()
TMS=sys.argv[1]
t=parse(TMS);tape={};p=0;q=0
snap={}
# detect translated cycler: at each time head sets a new left record, record (state, right-window pattern of 40 cells)
lo=0;found=None
for n in range(400000):
    r=t[(q,tape.get(p,0))]
    if r is None: print("halt at",n);break
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
    if p<lo:
        lo=p
        win=tuple(tape.get(p+i,0) for i in range(60))
        key=(q,win)
        if key in snap and found is None:
            found=(snap[key],n,snap[key]); print("record repeat: steps",snap[key],"->",n,"period",n-snap[key])
        snap.setdefault(key,n)
print("done",n,p,len(tape))
