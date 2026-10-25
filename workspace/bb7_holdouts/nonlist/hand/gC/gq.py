"""gq.py MACHINE K SPEC MAXMACRO [--from=G] [--n=N] [--side=l|r] [--sep=00]: run ms.exe from SPEC (ex.py syntax) at
idle priority; at tape-end events (head side) print the tape head-first as groups split at SEP blocks; a group
of tokens '01^x 10^y' is shown as (x,y)-like compact text. Prints when groups with index >= G change."""
import re, subprocess, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
args=[a for a in sys.argv[1:] if not a.startswith('--')]; opts=dict(a[2:].split('=',1) if '=' in a else (a[2:],'1') for a in sys.argv[1:] if a.startswith('--'))
m,K,spec,mm=args[:4]; m=open(m).read().strip() if m.endswith('.txt') else m
G=int(opts.get('from','2')); SEP=opts.get('sep','00'); side=opts.get('side','r')
line=subprocess.run([sys.executable,'ex.py',spec],capture_output=True,text=True).stdout.strip()[2:]
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p=subprocess.Popen([ms,m,K,mm,(side+'0') if side in 'lr' else 'p'+opts.get('every','1'),'i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\pids.txt','a').write(f'{p.pid}\tgroupC\tms.exe gq\n')
p.stdin.write(line+'\n'); p.stdin.close()
import atexit; atexit.register(lambda: p.kill())
NL=int(opts.get('n','100')); cnt=0; prev=None
def comp(gs):
    out=[];i=0
    while i<len(gs):
        best=None
        for per in (1,2,3):
            j=i
            while j+per<len(gs) and gs[j+per]==gs[j]: j+=1
            r=(j-i)//per+1
            if r>=3 and (best is None or r*per>best[0]*best[1]): best=(r,per)
        if best: r,per=best; out.append('{'+' | '.join(gs[i:i+per])+'}x%d'%r); i+=r*per
        else: out.append(gs[i]); i+=1
    return ' | '.join(out)
for l in p.stdout:
    if cnt>=NL: break
    if not l.startswith('T '): print(l.strip()); continue
    a,b=l.split('|',1); t=b.split()
    if side=='b' and not (t[0].startswith('[') or t[-1].startswith('[')): continue
    sd='L'
    ci=[i for i,x in enumerate(t) if x.startswith('[')][0]
    if ci>len(t)-1-ci: t=t[::-1]; sd='R'; ci=len(t)-1-ci
    if side!='e' and ci>0: continue
    t=t[:ci]+t[ci:]
    t=t[1:]; groups=[[]]
    for x in t:
        s,n=(x.split('^')+['1'])[:2]
        if s==SEP:
            for _ in range(int(n)): groups.append([])
        else: groups[-1].append(s if n=='1' else f'{s}^{n}')
    gs=[' '.join(g) if g else '-' for g in groups]
    key=tuple(gs[G:])
    if key!=prev:
        cnt+=1; prev=key; f=a.split(); print(f[1],f[2],sd,'|',comp(gs)[:int(opts.get('w','220'))])
