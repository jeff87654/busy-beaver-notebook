import idle, itertools, sys
def parse(m):
    rows=m.split('_'); return [[None if r[3*c]=='-' else (r[3*c],r[3*c+1],ord(r[3*c+2])-65) for c in (0,1)] for r in rows]
def trans(t,perm,mir):
    inv={o:i for i,o in enumerate(perm)}; out=[]
    for o in perm:
        row=[]
        for c in (0,1):
            v=t[o][c]
            row.append(None if v is None else (v[0], ('L' if v[1]=='R' else 'R') if mir else v[1], inv[v[2]]))
        out.append(row)
    return out
def diff(a,b): return sum(1 for i in range(7) for c in (0,1) if a[i][c]!=b[i][c] and not (a[i][c] is None and b[i][c] is None))
ver={}
for l in open('final_all_verdicts.tsv'):
    f=l.rstrip('\n').split('\t')
    if f[0]!='machine': ver[f[0]]=f[3]
for q in sys.argv[1:]:
    tq=parse(q); res=[]
    kn=[(k,parse(k)) for k in ver if k!=q]
    for perm in itertools.permutations(range(7)):
        for mir in (False,True):
            t2=trans(tq,perm,mir)
            for k,tk in kn:
                d=diff(t2,tk)
                if d<=2: res.append((d,k,chr(65+perm.index(0)),mir))
    res=sorted(set(res))[:6]
    print(q); [print('   d=%d %s start=%s mirror=%s  %s'%(d,k,s,mi,ver[k][:60])) for d,k,s,mi in res]
