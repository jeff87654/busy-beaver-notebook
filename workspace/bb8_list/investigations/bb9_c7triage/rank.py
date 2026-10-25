import idle
"""rank.py: heuristic structure ranking of the c7 w150 screen rows (HALT and STOP/END).
levelups = clears whose depth > 1.15 x running max (depth >= 30); grow_tail = max depth in last third > 1.15 x max before."""
import collections, sys
R='../bb9_redir/runs/'
def comp(zs):
    out=[]
    for k in zs:
        if out and out[-1][0]==k: out[-1][1]+=1
        else: out.append([k,1])
    return ' '.join(str(k) if c==1 else '%sx%d'%(k,c) for k,c in out)
rows=[]
for tag,f in [('u',R+'c7_1undef_w150_cnt.tsv'),('m',R+'c7_multi_w150_cnt.tsv')]:
    for l in open(f):
        p=l.rstrip('\n').split('\t')
        v=p[1].split(); zs=[int(x) for x in p[3].split()]
        kind=v[0]; slot=v[1] if kind=='HALT' else (v[-1] if kind=='STOP' else '')
        ones=v[v.index('ones')+1] if 'ones' in v else ''
        mx=0; ups=0; upl=[]
        for z in zs:
            if z>=30 and z>1.15*mx: ups+=1; upl.append(z)
            mx=max(mx,z)
        n=len(zs); a=zs[:max(1,2*n//3)]; b=zs[max(1,2*n//3):]
        gt = bool(b) and max(b) > 1.15*max(a+[1])
        rows.append(dict(tag=tag,m=p[0],kind=kind,slot=slot,ones=ones,zs=zs,ups=ups,upl=upl,mx=mx,gt=gt,line=p[1]))
def key(r): return (r['kind'], comp(r['zs']), r['slot'], r['ones'])
g=collections.OrderedDict()
for r in rows: g.setdefault(key(r),[]).append(r)
reps=[]
for k,rs in g.items():
    r=dict(rs[0]); r['twins']=[x['tag']+':'+x['m'] for x in rs]; reps.append(r)
def score(r): return (r['ups'], r['mx'])
with open('rank_all.tsv','w') as fo:
    for r in sorted(reps,key=lambda r:(r['kind']!='HALT',)+tuple(-x for x in score(r))):
        fo.write('\t'.join([r['kind'],r['slot'],r['ones'],str(r['ups']),str(r['mx']),'G' if r['gt'] else '-',str(len(r['twins'])),r['twins'][0],' '.join(map(str,r['upl'])),comp(r['zs'])[:200]])+'\n')
c=collections.Counter((r['kind'],min(r['ups'],6)) for r in reps)
print(sorted(c.items()))
print('STOP/END reps growing at tail:', sum(1 for r in reps if r['kind']!='HALT' and r['gt']))
