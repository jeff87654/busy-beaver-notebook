from lit import parse
import sys, threading, os
threading.Timer(90, lambda: os._exit(3)).start()
TMS=sys.argv[1]; NMAX=int(sys.argv[2])
t=parse(TMS);tape={};p=0;q=0
snap={};lo=0;last_rec=None;maxexc={}
# excursion: max over steps since last record of (p - lo)
exc=0
for n in range(NMAX):
    r=t[(q,tape.get(p,0))]
    if r is None: print("halt at",n);break
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
    exc=max(exc,p-lo)
    if p<lo:
        lo=p
        win=tuple(tape.get(p+i,0) for i in range(60))
        key=(q,win)
        if key in snap:
            n0,exc0=snap[key]
            print("record repeat: steps",n0,"->",n,"period",n-n0,"shift",'?', "max excursion right of previous record (cells):",exc)
            break
        snap[key]=(n,exc); exc=0
else:
    print("no repeat within",NMAX)
