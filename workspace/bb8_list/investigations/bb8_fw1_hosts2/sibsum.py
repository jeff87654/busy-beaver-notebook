import idle, collections
from ana import load, kind
from formC import forms
from fam import SIB, BASES
for nm in SIB:
  for mode in '78':
    labs,V=load(nm,mode); f=BASES[nm][3]
    c=collections.Counter()
    for m,outs in V:
        ks=''.join(kind(o,f) for o in outs); s=set(ks)-{'='}
        if s=={'H'}:
            if f=='C': c['H-allTOP' if all(ks[i]=='H' for i,l in enumerate(labs) if l[0].startswith('TOP t=1')) else 'H-partial']+=1
            else:
                odd=[i for i,l in enumerate(labs) if l[0].startswith('ABS') and int(l[0].split('=')[1])%2]
                ev=[i for i,l in enumerate(labs) if l[0].startswith('ABS') and int(l[0].split('=')[1])%2==0]
                c['H-allABS' if all(ks[i]=='H' for i in ev) else ('H-oddABS' if all(ks[i]=='H' for i in odd) else 'H-partial')]+=1
        elif s=={'M'}: c['M']+=1
        elif s=={'T'}: c['T']+=1
        else: c['mixed:'+''.join(sorted(s))]+=1
    if f=='C' and V:
        res,ex=forms(nm,mode); c['M-STD']=sum(v for k,v in res.items() if k.startswith('STD')); c['M-other']=sum(v for k,v in res.items() if not k.startswith('STD'))
    if V: print(nm,mode,dict(c))
