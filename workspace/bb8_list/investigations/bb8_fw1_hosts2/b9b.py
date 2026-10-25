import idle, collections, glob, os, re
from ana import load, kind
from fam import dec
for f in sorted(glob.glob('out/B[24].m9_*')):
    nm,mode=os.path.basename(f).split('.m'); labs,V=load(nm,mode)
    L=[l[0] for l in labs]; i31=L.index('ABS c=31'); i16=L.index('ABS c=16')
    c=collections.Counter()
    for m,outs in V:
        ks=''.join(kind(o,'B') for o in outs)
        if 'H' in [kind(outs[i],'B') for i,l in enumerate(L) if l.startswith('ABS') and int(l.split('=')[1])%2]: continue
        o=outs[i31]
        if o=='=': sh='base'
        elif o[0]!='M': sh=o[0]
        else:
            s=dec('B',o[1:]); sh=re.sub(r'\d\d+','N',s)
        anyH='H' in ks
        c[(sh,'anyH' if anyH else 'noH')]+=1
    print(nm,mode)
    for k,v in c.most_common(12): print('   %5d %s'%(v,k))
