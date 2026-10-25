import itertools
def load(f, pf=False):
    d={}
    for l in open(f):
        x=l.rstrip('\n').split('\t')
        if l.startswith(('#','machine')) or len(x)<11: continue
        d[x[0]]=dict(p2=float(x[3]),nsr=int(x[9]),sr0=float(x[10]),mc=int(x[8]))
    return d
def lpf(f):
    d={}
    for l in open(f):
        x=l.rstrip('\n').split('\t')
        if len(x)<11 or x[0]=='machine': continue
        d[x[0]]=dict(pass_=x[1]=='PASS',span=int(x[3]),cs=int(x[6]),csn=int(x[7]),res=int(x[10]),mb=int(x[5]))
    return d
C=load('rej/ctl_p.tsv'); S=load('rej/samp_p.tsv'); PC=lpf('rej/ctl_pf7.tsv'); PS=lpf('rej/samp_pf7.tsv')
for m in C: C[m].update(PC.get(m,{}))
for m in S: S[m].update(PS.get(m,{}))
P='../../bb8_list/investigations/pocket_rescreen/'
gap={}
for l in open(P+'gapcls_r1lg.tsv'):
    x=l.rstrip('\n').split('\t'); gap[x[0]]=x[1].split('(')[0]
ctl=[l.split()[0] for f in ['../cal.txt','c8.txt','rk63.txt','pf7chk/f0ld.txt','pf7chk/pair.txt','pf7chk/n2.txt','pf7chk/t14core.txt'] for l in open(f) if '_' in l]
ctl+= [m for m,k in gap.items() if k in ('GAP-GROWS','MULTI-GAP','UNARY-GAP')]
ctl=[m for m in set(ctl) if m in C and not C[m].get('pass_',True)]   # controls that pf7 rejects
print('controls rejected by pf7:', len(ctl))
best=[]
for a in [7.0,7.25,7.5,7.75,8.0]:
  for b in [1,2,3,4,99]:
    for c in [0,0.3,0.5,99]:      # cs fraction cs/csn
      for d in [99,8,4]:           # pf7 RESETS
        fn=lambda x: x['p2']>=a or x['nsr']>=b or (x.get('csn',0)>0 and x.get('cs',0)>=c*max(x['csn']-1,1) and x.get('cs',0)>=5) or x.get('res',0)>=d
        miss=sum(not fn(C[m]) for m in ctl); rate=sum(fn(x) for x in S.values())/len(S)
        best.append((miss,rate,a,b,c,d))
best.sort()
for r in best[:12]: print(r)
