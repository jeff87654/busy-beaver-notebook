import idle, sys, collections, random
from ana import load, kind
from fam import BASES, dec, run
# for T-outcome variants: rerun the first T test with a large budget, report outcome
nm,mode=sys.argv[1:3]; N=int(sys.argv[3]) if len(sys.argv)>3 else 3*10**7
f=BASES[nm][3]; labs,V=load(nm,mode)
tapes=[l.split()[0] for l in open('bat/%s.rare'%nm)]
c=collections.Counter(); ex={}
for m,outs in V:
    ks=''.join(kind(o,f) for o in outs)
    if 'T' not in ks: continue
    i=ks.index('T')
    r=run(m,BASES[nm][1],BASES[nm][2],[tapes[i]],N,1,f)[0][0]
    if r.startswith('M'): k='M-late'; d=dec(f,r.split()[3])[:50]
    else: k=r.split()[0]; d=r[:60]
    c[k]+=1; ex.setdefault(k,[]).append((m,labs[i][0],d))
print(nm,mode,dict(c))
for k in ex:
    for e in ex[k][:4]: print('  ',k,e)
