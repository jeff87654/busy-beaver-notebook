import idle, json, os, subprocess, sys, collections
HERE=os.path.dirname(os.path.abspath(__file__)); REB=os.path.abspath(os.path.join(HERE,'..','..'))
T=collections.OrderedDict()
for l in open(os.path.join(HERE,'t_all.tsv')):
    f=l.rstrip('\n').split('\t')
    if f[1]=='NONE': T.setdefault(f[0],[]); continue
    T.setdefault(f[0],[]).append(f[1])
def done(path):
    r={}
    if os.path.exists(path):
        for l in open(path):
            d=json.loads(l); r[d['machine']]=d
    return r
def run(cmd):
    p=subprocess.Popen(cmd,cwd=REB,creationflags=0x40)
    with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d %s\n'%(p.pid,' '.join(cmd[:3])))
    p.wait()
settled={}
for k in range(3):
    pool=os.path.join(HERE,'pool_a%d.tsv'%k); out=os.path.join(HERE,'res_a%d.jsonl'%k)
    rows=[(m,ts[k]) for m,ts in T.items() if len(ts)>k and m not in settled]
    with open(pool,'w') as f:
        f.write('machine\ttemplate\tgrade\tsources\tcls\n')
        for m,t in rows: f.write('%s\t%s\t-\tpf\t-\n'%(m,t))
    if rows: run([sys.executable,'reb7.py',pool,out])
    for m,d in done(out).items():
        v=d.get('verdict','')
        if not v.startswith('NOFIT') and 'ERR' not in v: settled[m]=(k,d)
    print('attempt',k,'settled so far',len(settled),flush=True)
with open(os.path.join(HERE,'summary1.tsv'),'w') as f:
    for m in T:
        if m in settled: k,d=settled[m]; f.write('%s\t%s\t%s\t%s\n'%(m,d.get('tmpl'),d.get('verdict'),d.get('growth')))
        else: f.write('%s\t-\tNOFIT\t-\n'%m)
