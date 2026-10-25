# summ.py leaf files... : summary of m9s LEAF lines
import sys, collections
H=[]; B=[]
for fn in sys.argv[1:]:
    for l in open(fn):
        f=l.split()
        if not f or f[0]!='LEAF': continue
        d=dict(m=f[1],st=f[2],out=f[3],steps=int(f[4]),sig=int(f[5]),span=int(f[6]),jumps=int(f[7]),maxj=int(f[8]),appr=int(f[9]),nrep=int(f[11]) if len(f)>11 else int(f[9]),repj=f[12] if len(f)>12 else '')
        (H if d['out']=='HALT' else B).append(d)
print('halters',len(H),'holdouts',len(B))
print('halters with REP jumps:',sum(1 for d in H if d['nrep']>0))
H.sort(key=lambda d:(d['nrep'],d['maxj'],d['sig']),reverse=True)
for d in H[:15]: print('  H',d['m'],d['st'],'steps',d['steps'],'sig',d['sig'],'jumps',d['jumps'],'maxj',d['maxj'],'nrep',d['nrep'],d['repj'])
c=collections.Counter()
for d in B:
    k=(d['out'],'nojump' if d['jumps']==0 else ('norep' if d['nrep']==0 else 'rep%d'%min(d['nrep'],9)))
    c[k]+=1
for k,v in sorted(c.items()): print('  B',k,v)
B.sort(key=lambda d:(d['nrep'],d['jumps']),reverse=True)
for d in B[:15]: print('  B',d['m'],d['st'],d['out'],'steps',d['steps'],'sig',d['sig'],'span',d['span'],'jumps',d['jumps'],'maxj',d['maxj'],'nrep',d['nrep'],d['repj'])
