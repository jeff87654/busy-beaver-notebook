import idle, sys, subprocess, os, collections
RK7=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rk7.exe'
HERE=os.path.dirname(os.path.abspath(__file__))
HITS=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\prefilter\hits_dl2_1M.tsv'
SS=['-','0','1','00','01','10','11','001','010','011','100','101','110','111','0011','1001','1011']
def trace(m,O,Q,P,u,s,S,N=3000000,maxk=400):
    args=[RK7,'trace',m,O,Q,P,u,s,'1','0','1','0',S,str(N),str(maxk)]
    p=subprocess.Popen(args,stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d rk7.exe\n'%p.pid)
    out,_=p.communicate()
    ks=[]
    for ln in out.splitlines():
        f=ln.split()
        if f and f[0]=='K': ks.append(([] if f[2]=='-' else [int(x) for x in f[2].split(',')],int(f[3]),int(f[4])))
    return ks
def score(ks):
    if len(ks)<10: return 0
    L=[len(k[0]) for k in ks]
    good=sum(1 for k in ks if len(k[0])>=1)
    # diversity of last-digit values & lengths
    return good*min(4,len(set(L)))*min(10,len(set(k[2] for k in ks)))
def coding(vals):
    for al,be in ((2,0),(2,1),(3,0),(3,1),(3,2),(1,0)):
        if vals and all(v>=be and (v-be)%al==0 for v in vals): return '%d%s+%d'%(al,'%s',be)
    return '1%s+0'
if __name__!="__main__": raise SystemExit
rows=[l.split()[0] for l in open(sys.argv[1]) if l.startswith("1RB")]
hits={}
for l in open(HITS):
    f=l.rstrip('\n').split('\t')
    if f[0] in rows: hits[f[0]]=f[6].split(';') if len(f)>6 else []
out=open(sys.argv[2],'a')
for m in rows:
    base=collections.OrderedDict()
    for t in hits.get(m,[]):
        if not t or t=='-': continue
        kv=dict(x.split('=',1) for x in t.split(',')[2:])
        O,Q=t.split(',')[:2]
        base[(O,Q,kv['P'],kv['u'],kv['s'])]=1
    best=[]
    for (O,Q,P,u,s) in base:
        for S in SS:
            ks=trace(m,O,Q,P,u,s,S)
            sc=score(ks)
            if sc: best.append((sc,O,Q,P,u,s,S,ks))
    best.sort(key=lambda x:-x[0])
    if not best: out.write('%s\tNONE\n'%m); out.flush(); print(m,'NONE',flush=True); continue
    for sc,O,Q,P,u,s,S,ks in best[:3]:
        dv=[d for k in ks for d in k[0]]; av=[k[1] for k in ks]; bv=[k[2] for k in ks]
        dc=coding(dv)%'d'; bc=coding(bv)%'b'
        tm='%s,%s,P=%s,u=%s,s=%s,d=%s,b=%s,S=%s'%(O,Q,P,u,s,dc,bc,S)
        out.write('%s\t%s\t%d\t%d\n'%(m,tm,sc,len(ks))); out.flush()
        print(m,tm,sc,len(ks),flush=True)
