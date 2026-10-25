import sys
def lg(f):
    d={}
    for l in open(f):
        x=l.rstrip('\n').split('\t')
        if l.startswith(('#','machine')) or len(x)<12: continue
        d[x[0]]=dict(h=int(x[1]),G=int(x[3]),nres=int(x[5]),RZ=int(x[7]),RO=int(x[8]),RB=int(x[9]),t0=int(x[10]),t2=int(x[11]))
    return d
C=lg(sys.argv[1]); S=lg(sys.argv[2])
P='../../bb8_list/investigations/pocket_rescreen/'
gap={}
for l in open(P+'gapcls_r1lg.tsv'):
    x=l.rstrip('\n').split('\t'); gap[x[0]]=x[1].split('(')[0]
pf={}
for l in open('rej/ctl_pf7.tsv'):
    x=l.split('\t')
    if len(x)>2 and x[0]!='machine': pf[x[0]]=x[1]=='PASS'
cls={n:[l.split()[0] for l in open(f) if '_' in l] for n,f in [('cal','../cal.txt'),('c8','c8.txt'),('rk63','rk63.txt'),('f0ld','pf7chk/f0ld.txt'),('pair','pf7chk/pair.txt'),('n2','pf7chk/n2.txt'),('t14core','pf7chk/t14core.txt')]}
for k in ('GAP-GROWS','MULTI-GAP','UNARY-GAP','NOGAP','OTHER'): cls[k]=[m for m,v in gap.items() if v==k]
cls['gap_pf7miss']=[m for m,v in gap.items() if v in('GAP-GROWS','MULTI-GAP','UNARY-GAP') and not pf.get(m,True)]
tests={'RZ>=2':lambda x:x['RZ']>=2,'RZ>=2|RO>=2':lambda x:x['RZ']>=2 or x['RO']>=2,'RZ>=3|RO>=3':lambda x:x['RZ']>=3 or x['RO']>=3,
 'G>=2':lambda x:x['G']>=2,'G>=3':lambda x:x['G']>=3,'(RZ|RO)>=2&G>=2':lambda x:(x['RZ']>=2 or x['RO']>=2) and x['G']>=2,
 'RB>=2':lambda x:x['RB']>=2,'nres>=2':lambda x:x['nres']>=2,'halt':lambda x:x['h']>=0}
for t,fn in tests.items():
    r=' '.join(f"{k}:{sum(fn(C[m]) for m in v if m in C)}/{sum(1 for m in v if m in C)}" for k,v in cls.items())
    print(f"{t:18s} rej {sum(fn(x) for x in S.values())/len(S):.3f} | {r}")
