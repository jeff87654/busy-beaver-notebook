import idle, collections, glob, os
from ana import load, kind
for f in sorted(glob.glob('out/B*.m9_*'))+sorted(glob.glob('out/B*.m8')):
    nm,mode=os.path.basename(f).split('.m'); labs,V=load(nm,mode)
    absodd=[i for i,l in enumerate(labs) if l[0].startswith('ABS') and int(l[0].split('=')[1])%2==1]
    c=collections.Counter(); ex=[]
    for m,outs in V:
        ks=[kind(outs[i],'B') for i in absodd]
        h=sum(k=='H' for k in ks)
        if h==0: c['noH-oddABS']+=1
        elif h==len(ks): c['H-all-oddABS']+=1
        else: c['H-partial']+=1; ex.append((m,''.join(ks)))
    print(nm,mode,dict(c))
    for e in ex[:5]: print('    ',e, [labs[i][0] for i in absodd])
