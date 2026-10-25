import idle, sys, subprocess, os
from surg import snapshot, expand
HERE=os.path.dirname(os.path.abspath(__file__))
# surg2 M step side "old1=>new1;;old2=>new2" W N [S0]
M,step,side,reps,W,N=sys.argv[1:7]; S0=sys.argv[7] if len(sys.argv)>7 else '0'
h,s=snapshot(M,int(step),side)
print('snap',h,s[:220])
for r in reps.split(';;'):
    a,b=r.split('=>'); assert a in s, a; s=s.replace(a,b,1)
print('new ',s[:220])
bits=''.join(expand(t) for t in s.split())
init=(h[2]+':'+bits[:-1]) if side=='R' else (h[2]+'<'+bits[1:])
fn=os.path.join(HERE,'init_%d.txt'%os.getpid()); open(fn,'w').write(init)
p=subprocess.Popen([os.path.join(HERE,'tcyc2.exe'),M,S0,N,W,'R',fn],stdout=subprocess.PIPE,text=True,creationflags=0x40)
with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d tcyc2.exe\n'%p.pid)
print(p.communicate()[0].strip()); os.remove(fn)
