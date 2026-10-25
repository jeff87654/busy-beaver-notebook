import idle, collections, glob, os
from ana import load, kind
from formC import forms
tot=collections.Counter(); nonstd=[]
for f in sorted(glob.glob('out/C*.m9_*')):
    nm,mode=os.path.basename(f).split('.m'); 
    labs,V=load(nm,mode)
    c=collections.Counter()
    for m,outs in V:
        ks=''.join(kind(o,'C') for o in outs); s=set(ks)-{'='}
        if s=={'H'}:
            # all TOP t=1 tests halt?
            allt=all(ks[i]=='H' for i,l in enumerate(labs) if l[0].startswith('TOP t=1'))
            c['H-allTOP' if allt else 'H-partial']+=1
            if not allt: nonstd.append((nm,mode,m,'H-partial'))
        elif s=={'M'}: c['M']+=1
        elif s=={'T'}: c['T']+=1
        else: c['mixed:'+''.join(sorted(s))]+=1; nonstd.append((nm,mode,m,''.join(sorted(s))))
    res,ex=forms(nm,mode)
    std=sum(v for k,v in res.items() if k.startswith('STD')); oth=sum(v for k,v in res.items() if not k.startswith('STD'))
    c['M-STD']=std; c['M-other']=oth
    for k,e in ex.items():
        for x in e: nonstd.append((nm,mode,x[0],k))
    print(nm,mode,dict(c)); tot.update(c)
print('TOTAL',dict(tot))
print('non-standard:',len(nonstd))
for x in nonstd[:40]: print('  ',x)
