import idle, sys, subprocess, os
from surg import snapshot, expand
from evlog2 import rruns, pcomp
HERE=os.path.dirname(os.path.abspath(__file__))
M,step,side,target,rep,N,ratio=sys.argv[1:8]
h,s=snapshot(M,int(step),side)
s2=s.replace(target,rep if rep!='-' else '',1)
bits=''.join(expand(t) for t in s2.split())
init=(h[2]+':'+bits[:-1]) if side=='R' else (h[2]+'<'+bits[1:])
fn=os.path.join(HERE,'init_%d.txt'%os.getpid()); open(fn,'w').write(init)
p=subprocess.Popen([os.path.join(HERE,'ev.exe'),M,N,'1000000000000','B','1',fn],stdout=subprocess.PIPE,text=True,creationflags=0x40)
with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d ev.exe\n'%p.pid)
nxt=0; ratio=float(ratio)
for l in p.stdout:
    if '|' not in l: print(l.strip()); continue
    st=int(l.split()[0])
    if st<nxt: continue
    nxt=max(st*ratio,st+1)
    hh,r=l.split('|'); print(hh.strip(),'|',pcomp(rruns(r))[:260],flush=True)
os.remove(fn)
