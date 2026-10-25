import idle, sys, subprocess, os
from surg import snapshot, expand
HERE=os.path.dirname(os.path.abspath(__file__))
M,step,side,target,repls,W,N=sys.argv[1:8]
h,s=snapshot(M,int(step),side)
print('snap',h,s[:200])
for rep in repls.split(','):
    s2=s.replace(target,rep if rep!='-' else '',1)
    bits=''.join(expand(t) for t in s2.split())
    q=h[2]
    if side=='R': init=q+':'+bits[:-1]; tside='R'
    else: init=q+'<'+bits[1:]; tside='R'
    tf=os.path.join(HERE,'init.txt')
    r=subprocess.run([os.path.join(HERE,'tcyc.exe'),M,'0',N,W,tside,init],capture_output=True,text=True,creationflags=0x40)
    print(target,'->',rep,':',' || '.join(r.stdout.strip().splitlines()[-2:]))
