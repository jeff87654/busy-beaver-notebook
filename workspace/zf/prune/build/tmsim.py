"""Minimal simulator for Wade's .tm format (state read write dir next). Prints tape at each visit of a watch state."""
import sys, re
def load(path):
    start=None; tbl={}
    for l in open(path, encoding='utf-8'):
        l=l.strip()
        if l.startswith('#!'):
            p=l[2:].split()
            if p and p[0]=='start': start=p[1]
        elif l and not l.startswith('#'):
            s,r,w,d,n=l.split()
            tbl[(s,r)]=(w,d,n)
    return start,tbl
def run(path, watch, maxsteps, maxvisits, show=None):
    start,tbl=load(path)
    tape={}; pos=0; st=start; steps=0; visits=0
    while steps<maxsteps:
        if st==watch or (show and st in show):
            visits+=1
            lo=min(tape)-1 if tape else -1; hi=max(tape)+1 if tape else 1
            s=''.join(('[' if i==pos else '')+tape.get(i,'0')+(']' if i==pos else '') for i in range(lo,hi+1))
            print(f"{steps:8d} {st:28s} {s}")
            if visits>=maxvisits: return
        t=tbl.get((st,tape.get(pos,'0')))
        if t is None:
            print(f"HALT at step {steps} state {st}"); return
        w,d,n=t; tape[pos]=w; pos+= 1 if d=='R' else -1; st=n; steps+=1
if __name__=='__main__':
    path=sys.argv[1]; watch=sys.argv[2]; maxsteps=int(sys.argv[3]); maxvisits=int(sys.argv[4])
    show=set(sys.argv[5].split(',')) if len(sys.argv)>5 else None
    run(path,watch,maxsteps,maxvisits,show)
