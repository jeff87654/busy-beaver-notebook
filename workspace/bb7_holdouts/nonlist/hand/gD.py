"""g.py MACHINE K MODE 'TAPE' MAXMACRO [--drop=k] [--n=lines] [--t=sec] [--sep=00] [--w=]: ms.exe from a tape spec
('Q side | toks', (a b)xN allowed); at events print groups (split at SEP) when groups[:-drop] change."""
import re, subprocess, sys, threading, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
a=[x for x in sys.argv[1:] if not x.startswith('--')]; o=dict((x[2:].split('=')+['1'])[:2] for x in sys.argv[1:] if x.startswith('--'))
m,K,mode,spec,mm=a[:5]; DROP=int(o.get('drop','2')); NL=int(o.get('n','60')); SEP=o.get('sep','00'); W=int(o.get('w','220'))
def expand(s):
    while '(' in s: s=re.sub(r'\(([^()]*)\)x(\d+)', lambda g: ' '.join([g.group(1)]*int(g.group(2))), s)
    return s
h,b=spec.split('|',1); inp=h+'| '+expand(b)+'\n'
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p=subprocess.Popen([ms,m,K,mm,mode,'i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\pids.txt','a').write(f'{p.pid}\tgroupD\tms.exe g\n')
threading.Timer(float(o.get('t','60')), lambda: p.poll() is None and p.kill()).start()
p.stdin.write(inp); p.stdin.close()
prev=None; cnt=0; last=None
for l in p.stdout:
    if not l.startswith('T '):
        print(l.strip()); continue
    if '|' not in l: continue
    x,y=l.split('|',1); t=[s for s in y.split() if not s.startswith('[')]
    gr=[[]]
    for s in t:
        q,n=(s.split('^')+['1'])[:2]; n=int(n)
        if q==SEP and n<=int(o.get('sepmax','999999')):
            for _ in range(n): gr.append([])
        else: gr[-1].append(q if n==1 else f'{q}^{n}')
    gs=['.'.join(g) if g else '-' for g in gr]
    out=[];i=0
    while i<len(gs):
        j=i
        while j+1<len(gs) and gs[j+1]==gs[i]: j+=1
        out.append(gs[i] if j==i else f'[{gs[i]}]x{j-i+1}'); i=j+1
    key=' | '.join(gs[:-DROP]) if DROP else ' | '.join(gs)
    if 'acc' in o:
        ix=[i for i,g in enumerate(gs) if o['acc'] in g]; key=' | '.join(gs[:ix[0]-int(o.get('accb','0'))]) if ix else key
    f=x.split(); s=f'{f[1]} {f[2]} {f[3]} : '+' | '.join(out)
    last=s[:W]
    if key!=prev:
        print(last); prev=key; cnt+=1
        if cnt>=NL: break
print('LAST', last)
if p.poll() is None: p.kill()
