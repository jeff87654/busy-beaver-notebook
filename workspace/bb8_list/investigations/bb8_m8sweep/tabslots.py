import json,glob,collections,sys
d=json.load(open('pool.json'))['pool']
ms=sorted(d)
out=[]
c=collections.Counter()
for i,m in enumerate(ms):
    try: l=open('slots/%03d.txt'%i).read().strip().splitlines()[-1]
    except Exception: c['missing']+=1; continue
    f=l.split(); kv={x.split('=',1)[0]:x.split('=',1)[1] for x in f if '=' in x}
    kind=f[1]; halt=f[2] if kind=='HALT' else ''
    out.append((m,kind,halt,kv.get('esc'),kv.get('J'),kv.get('exhonly'),kv.get('lexhonly','?'),kv.get('guard','?'),kv.get('zeros','')))
    c[(kind, 'exhonly' if kv.get('exhonly','-')!='-' else '-')]+=1
for k,v in sorted(c.items(),key=str): print(v,k)
hs=collections.Counter((o[1],o[2],o[3]) for o in out if o[1]=='HALT')
print(hs.most_common(30))
