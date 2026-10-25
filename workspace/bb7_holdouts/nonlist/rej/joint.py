def lg(f):
    d={}
    for l in open(f):
        x=l.rstrip('\n').split('\t')
        if l.startswith(('#','machine')) or len(x)<12: continue
        d[x[0]]=dict(G=int(x[3]),nres=int(x[5]),mp=int(x[6]),RZ=int(x[7]),RO=int(x[8]),RB=int(x[9]),span=int(x[2]))
    return d
def lp(f):
    d={}
    for l in open(f):
        x=l.rstrip('\n').split('\t')
        if l.startswith(('#','machine')) or len(x)<11: continue
        d[x[0]]=dict(p2=float(x[3]),nsr=int(x[9]),mc=int(x[8]))
    return d
C=lg('rej/ctl_g.tsv'); S=lg('rej/s4k_g.tsv'); CP=lp('rej/ctl_p.tsv'); SP=lp('rej/samp_p.tsv')
for m in C: C[m].update(CP.get(m,{}))
S={m:dict(v,**SP[m]) for m,v in S.items() if m in SP}
P='../../bb8_list/investigations/pocket_rescreen/'
gap={l.split('\t')[0]:l.rstrip('\n').split('\t')[1].split('(')[0] for l in open(P+'gapcls_r1lg.tsv')}
ctl=[l.split()[0] for f in ['../cal.txt','../h14.txt','c8.txt','rk63.txt','pf7chk/f0ld.txt','pf7chk/pair.txt','pf7chk/n2.txt'] for l in open(f) if '_' in l]+[m for m,k in gap.items() if k in('GAP-GROWS','MULTI-GAP','UNARY-GAP')]
ctl=[m for m in set(ctl) if m in C]
res=[]
for nr in (6,8,10,13):
  for mp in (0,16,20,32,64):
    for p2 in (7.0,7.5,8.0,99):
      for ns in (1,2,4,999):
        fn=lambda x: x['nres']>=nr and (x['mp']>=mp or x['p2']>=p2 or x['nsr']>=ns)
        miss=sum(not fn(C[m]) for m in ctl); rate=sum(fn(x) for x in S.values())/len(S)
        res.append((miss,round(rate,3),nr,mp,p2,ns))
res.sort()
for r in [r for r in res if r[0]==0][:8]: print(r)
for r in sorted(res,key=lambda r:(r[1]))[:5]: print('low-rate',r)
