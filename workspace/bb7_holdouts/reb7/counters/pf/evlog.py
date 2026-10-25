import idle, sys, subprocess, os
from evp import unrle, runs, comp
HERE=os.path.dirname(os.path.abspath(__file__))
M,N,side,u,ratio,start=sys.argv[1:7]; ratio=float(ratio); nxt=float(start)
p=subprocess.Popen([os.path.join(HERE,'ev.exe'),M,N,'1000000000000',side,'1'],stdout=subprocess.PIPE,text=True,creationflags=0x40)
with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d ev.exe\n'%p.pid)
for l in p.stdout:
    if '|' not in l: print(l.strip(),flush=True); continue
    st=int(l.split()[0])
    if st<nxt: continue
    nxt=st*ratio
    h,r=l.split('|'); print(h.strip(),'|',comp(runs(unrle(r),u))[:300],flush=True)
