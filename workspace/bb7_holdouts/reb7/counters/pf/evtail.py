import idle, sys, subprocess, os, re
from evp import unrle, runs, comp
HERE=os.path.dirname(os.path.abspath(__file__))
M,N,side,u=sys.argv[1:5]; skip=int(sys.argv[5]) if len(sys.argv)>5 else 2
p=subprocess.Popen([os.path.join(HERE,'ev.exe'),M,N,'1000000000000',side,'1'],stdout=subprocess.PIPE,text=True,creationflags=0x40)
with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d ev.exe\n'%p.pid)
last=None
for l in p.stdout:
    if '|' not in l: print(l.strip()); continue
    h,r=l.split('|'); s=comp(runs(unrle(r),u)); t=s.split(' ')
    # key = tokens with the first `skip` numbers replaced by #
    k=[];n=0
    for x in t:
        if re.fullmatch(r'\d+',x) and n<skip: k.append('#'); n+=1
        else: k.append(x)
    key=' '.join(k)
    if key!=last:
        try: print(h.strip(),"|",s[:260],flush=True)
        except OSError: pass
        last=key
