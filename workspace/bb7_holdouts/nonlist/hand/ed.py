"""e.py MACHINE K MODE SPEC MAXMACRO [IDX=VAL ...] [LIST=n] [--skip=k|--drop=k] [--n=] [--t=] [--w=] [--shape]
SPEC = 'Q s | toks' (with (a b)xN) or @DUMPFILE (line 2). IDX edits = token index after '|' ([cur] = 0).
Prints compressed tape when tokens[skip:] (L events) / tokens[:-drop] change, or (--shape) when count-erased tape changes."""
import re, subprocess, sys, threading
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
a=[x for x in sys.argv[1:] if not x.startswith('--')]; o=dict((x[2:].split('=')+['1'])[:2] for x in sys.argv[1:] if x.startswith('--'))
m,K,mode,spec,mm=a[:5]; edits=a[5:]
def expand(s):
    while '(' in s: s=re.sub(r'\(([^()]*)\)x(\d+)', lambda g: ' '.join([g.group(1)]*int(g.group(2))), s)
    return s
line=open(spec[1:]).read().splitlines()[1] if spec.startswith('@') else spec
h,b=line.split('|',1); toks=expand(b).split()
for e in edits:
    k,v=e.split('=')
    if k=='LIST':
        best=(0,0); i=0
        while i+3<len(toks):
            j=i
            while j+3<len(toks) and toks[j]==toks[j+2] and toks[j+1]==toks[j+3]: j+=2
            if (j-i)//2+1>best[1]: best=(i,(j-i)//2+1)
            i=j+1 if j>i else i+1
        s,r=best; toks=toks[:s+2*int(v)]+toks[s+2*r:]
    else:
        i=int(k); bb=toks[i].split('^')[0]; toks[i]=f'{bb}^{v}'
inp=h+'| '+' '.join(toks)+'\n'
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p=subprocess.Popen([ms,m,K,mm,mode,'i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\pids.txt','a').write(f'{p.pid}\tgroupD\tms.exe e\n')
threading.Timer(float(o.get('t','60')), lambda: p.poll() is None and p.kill()).start()
p.stdin.write(inp); p.stdin.close()
def comp(ts):
    out=[];i=0
    while i<len(ts):
        best=None
        for L in (1,2,3,4,5,6):
            if i+2*L<=len(ts) and ts[i:i+L]==ts[i+L:i+2*L]:
                j=i
                while j+2*L<=len(ts) and ts[j+L:j+2*L]==ts[i:i+L]: j+=L
                n=(j-i)//L+1
                if best is None or n*L>best[1]*best[0]: best=(L,n)
        if best and best[1]>=2: L,n=best; out.append('('+' '.join(ts[i:i+L])+f')x{n}'); i+=L*n
        else: out.append(ts[i]); i+=1
    return ' '.join(out).replace('^1 ',' ').replace('^1)',')')
SK=int(o.get('skip','0')); DR=int(o.get('drop','0')); W=int(o.get('w','260')); NL=int(o.get('n','40'))
prev=None; cnt=0; last=None
for l in p.stdout:
    if not l.startswith('T '): print(l.strip()); continue
    if '|' not in l: continue
    x,y=l.split('|',1); t=y.split()
    if 'shape' in o:
        r=[re.sub(r'\^\d+|\[|\]','',s) for s in t]; r=[s for i,s in enumerate(r) if i==0 or s!=r[i-1]]; key=' '.join(r)
    else:
        tt=[s for s in t if not s.startswith('[')]; key=' '.join(tt[SK:len(tt)-DR])
        if 'key' in o:
            ks=[i for i,s in enumerate(tt) if s.startswith(o['key'])]; key=' '.join(tt[ks[0]:]) if ks else key
        if 'cnt' in o: key=key+' #'+str(tt.count(o['cnt']))
        if 'pat' in o:
            import re as _r; js=' '.join(tt).replace('^1 ',' ')+' '; key=' '.join(str(len(_r.findall(pp,js))) for pp in o['pat'].split(','))
    f=x.split(); s=f'{f[1]} {f[2]} {f[3]} | {comp(t)}'
    last=s if len(s)<=W else s[:W//3]+' ... '+s[-2*W//3:]
    if key!=prev:
        print(last); prev=key; cnt+=1
        if cnt>=NL: break
print('LAST',last)
if p.poll() is None: p.kill()
