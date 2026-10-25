import idle, sys, collections
from ana import load, kind
from fam import BASES
for nm in sys.argv[2:]:
    labs,V=load(nm,sys.argv[1]); f=BASES[nm][3]
    c=collections.Counter()
    for m,outs in V:
        ty=set()
        for i,o in enumerate(outs):
            if o!='=': ty.add(labs[i][0].split()[0]+':'+kind(o,f))
        c[' '.join(sorted(ty))]+=1
    print(nm)
    for k,v in c.most_common(): print('   %4d  %s'%(v,k))
