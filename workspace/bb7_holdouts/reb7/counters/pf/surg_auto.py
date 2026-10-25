import idle, sys, subprocess, os, re
from surg import snapshot, expand
HERE=os.path.dirname(os.path.abspath(__file__))
# for each row: snapshot at 1e8 (side of growth), counter=smallest (01)/(10) group with 5<=N<=40 -> removed, largest group -> Y, 2nd largest -> 1
rows=[l.strip() for l in open(sys.argv[1]) if l.strip()]
Y=int(sys.argv[2]); N=sys.argv[3]; W=sys.argv[4]
for m in rows:
    res=None
    for side in ('R','L'):
        h,s=snapshot(m,100000000,side)
        if h is None: continue
        toks=s.split()
        grp=[(i,int(re.fullmatch(r'\((?:01|10)\)x(\d+)',t).group(1))) for i,t in enumerate(toks) if re.fullmatch(r'\((?:01|10)\)x(\d+)',t)]
        if len(grp)<3: continue
        big=sorted(grp,key=lambda x:-x[1])
        cnt=[g for g in grp if 5<=g[1]<=40]
        if not cnt: continue
        c=cnt[0]
        t2=list(toks)
        t2[big[0][0]]=re.sub(r'x\d+','x%d'%Y,t2[big[0][0]]); t2[big[1][0]]=re.sub(r'x\d+','x1',t2[big[1][0]]); t2[c[0]]=''
        bits=''.join(expand(t) for t in t2 if t)
        init=(h[2]+':'+bits[:-1]) if side=='R' else (h[2]+'<'+bits[1:])
        fn=os.path.join(HERE,'init_%d.txt'%os.getpid()); open(fn,'w').write(init)
        p=subprocess.Popen([os.path.join(HERE,'tcyc2.exe'),m,'0',N,W,'R',fn],stdout=subprocess.PIPE,text=True,creationflags=0x40)
        with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d tcyc2.exe\n'%p.pid)
        out=p.communicate()[0].strip(); os.remove(fn)
        res='%s snap=%s counter=%d x,y=%d,%d -> Y=%d : %s'%(side,' '.join(h),c[1],big[1][1],big[0][1],Y,out)
        break
    print(m, res if res else 'NO-PATTERN', flush=True)
