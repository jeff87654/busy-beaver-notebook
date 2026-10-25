"""grp.py MACHINE K TAPE MAXMACRO [--from=G] : run ms.exe; at left-end events print the tape as groups split at '00'
blocks (each group shown compactly), printing when groups with index >= G (default 2) change."""
import re, subprocess, sys
args=[a for a in sys.argv[1:] if not a.startswith('--')]; opts=dict(a[2:].split('=') if '=' in a else (a[2:],'1') for a in sys.argv[1:] if a.startswith('--'))
m,K,tp,mm=args[:4]; G=int(opts.get('from','2')); SEP=opts.get('sep','00')
line = tp[2:] if tp.startswith('X:') else open(tp).read().splitlines()[1]
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p=subprocess.Popen([ms,m,K,mm,opts.get('mode','l0'),'i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
p.stdin.write(line+'\n'); p.stdin.close()
prev=None
import atexit; atexit.register(lambda: p.kill())
NL=int(opts.get('n','100')); cnt=0
for l in p.stdout:
    if cnt>=NL: break
    if not l.startswith('T '): print(l.strip()); continue
    a,b=l.split('|',1); t=b.split()
    if not t[0].startswith('['): continue
    t=t[1:]
    toks=[]
    for x in t:
        s,n=(x.split('^')+['1'])[:2]; toks.append((s,int(n)))
    groups=[[]]
    for s,n in toks:
        if s==SEP:
            for _ in range(n): groups.append([])
        else: groups[-1].append(s if n==1 else f'{s}^{n}')
    gs=['.'.join(g) if g else '-' for g in groups]
    # compress repeats
    out=[];i=0
    while i<len(gs):
        j=i
        while j+1<len(gs) and gs[j+1]==gs[i]: j+=1
        out.append(gs[i] if j==i else f'[{gs[i]}]x{j-i+1}'); i=j+1
    key=' | '.join(gs[G:]) if 'skel' not in opts else re.sub(r'\^\d+','',' | '.join(out))
    if key!=prev:
        s=a.split(); sys.stdout.write(f'{s[1]} {s[2]} {s[3]} : '+' | '.join(out)[:int(opts.get("w","200"))]+'\n'); sys.stdout.flush(); prev=key; cnt+=1
