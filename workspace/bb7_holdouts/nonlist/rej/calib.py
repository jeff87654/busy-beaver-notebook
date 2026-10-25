import collections, sys
def load(f):
    d={}
    for l in open(f):
        x=l.rstrip('\n').split('\t')
        if l.startswith(('#','machine')) or len(x)<11: continue
        d[x[0]]=dict(K=int(x[1]),p1=float(x[2]),p2=float(x[3]),npk=int(x[4]),mc=int(x[8]),nsr=int(x[9]),sr0=float(x[10]))
    return d
C=load('rej/ctl_p.tsv'); S=load(sys.argv[1] if len(sys.argv)>1 else 'rej/samp_p.tsv')
P='../../bb8_list/investigations/pocket_rescreen/'
cls={}
for name,f in [('cal',['../cal.txt']),('h14',['../h14.txt']),('c8',['c8.txt']),('rk63',['rk63.txt']),('famT14',[P+'famT14/roots1043.txt']),('fam0LD',['pf7chk/f0ld.txt']),('pair',['pf7chk/pair.txt']),('N2',['pf7chk/n2.txt'])]:
    cls[name]=[l.split()[0] for fn in f for l in open(fn) if '_' in l]
cls['T14miss']=[l.strip() for l in open('pf7chk/t14miss.txt')]
def rate(ms,fn):
    v=[C[m] for m in ms if m in C]; return f"{sum(fn(x) for x in v)}/{len(v)}"
tests={'P2>=8':lambda x:x['p2']>=8.0,'P2>=7.5':lambda x:x['p2']>=7.5,'P2>=7':lambda x:x['p2']>=7.0,'nsr>=2':lambda x:x['nsr']>=2,'nsr>=4':lambda x:x['nsr']>=4,'nsr>=8':lambda x:x['nsr']>=8}
for t,fn in tests.items():
    print(f"{t:9s} rejects {sum(fn(x) for x in S.values())/len(S):.3f} | "+' '.join(f"{k}:{rate(v,fn)}" for k,v in cls.items()))
print('P2 dist rejects', sorted(collections.Counter(round(x['p2']) for x in S.values()).items()))
print('T14miss P2', sorted(collections.Counter(round(C[m]['p2']) for m in cls['T14miss'] if m in C).items()))
print('T14miss nsr', sorted(collections.Counter(min(C[m]['nsr'],20) for m in cls['T14miss'] if m in C).items()))
print('rejects nsr', sorted(collections.Counter(min(x['nsr'],20) for x in S.values()).items()))
def lpf(f):
    d={}
    for l in open(f):
        x=l.rstrip('\n').split('\t')
        if len(x)<11 or x[0]=='machine': continue
        d[x[0]]=dict(pass_=x[1]=='PASS',span=int(x[3]),snaps=int(x[4]),mb=int(x[5]),cs=int(x[6]),csn=int(x[7]),res=int(x[10]))
    return d
PC=lpf('rej/ctl_pf7.tsv'); PS=lpf('rej/samp_pf7.tsv')
for m,v in C.items(): v.update(PC.get(m,{}))
for m,v in S.items(): v.update(PS.get(m,{}))
print('--- union signals (controls that pf7 FAILS counted only)')
for t,fn in {'res>=2':lambda x:x.get('res',0)>=2,'res>=3':lambda x:x.get('res',0)>=3,
             'P2>=7.5|nsr>=2|res>=3':lambda x:x['p2']>=7.5 or x['nsr']>=2 or x.get('res',0)>=3,
             'P2>=8|nsr>=4|res>=4':lambda x:x['p2']>=8 or x['nsr']>=4 or x.get('res',0)>=4,
             'P2>=7|nsr>=2|res>=2':lambda x:x['p2']>=7 or x['nsr']>=2 or x.get('res',0)>=2}.items():
    def r2(ms):
        v=[C[m] for m in ms if m in C and not C[m].get('pass_',False)]; return f"{sum(fn(x) for x in v)}/{len(v)}"
    print(f"{t:22s} rejects {sum(fn(x) for x in S.values())/len(S):.3f} | "+' '.join(f"{k}:{r2(v)}" for k,v in cls.items()))
miss=[m for k,v in cls.items() for m in v if m in C and not C[m].get('pass_',False) and not (C[m]['p2']>=7.5 or C[m]['nsr']>=2 or C[m].get('res',0)>=3)]
open('rej/ctl_miss.txt','w').write('\n'.join(miss)+'\n'); print('misses of union1', len(miss))
