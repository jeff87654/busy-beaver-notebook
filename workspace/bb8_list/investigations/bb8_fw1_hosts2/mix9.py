import idle, collections, glob, os, sys
from ana import load, kind
from fam import dec
groups=collections.defaultdict(list)
for f in sorted(glob.glob('out/C*.m9_*')):
    nm,mode=os.path.basename(f).split('.m'); labs,V=load(nm,mode)
    for m,outs in V:
        ks=''.join(kind(o,'C') for o in outs); s=set(ks)-{'='}
        if len(s)<2: continue
        # pattern over TOP t=1 and NOTOP tests: group label -> kinds
        pat=[]
        for i,l in enumerate(labs):
            if l[0].startswith('TOP t=1') or l[0].startswith('NOTOP'):
                pat.append(ks[i])
        groups[''.join(pat)].append((nm,mode,m))
labs=[l for l in load('C1','9_B00')[0] if l[0].startswith('TOP t=1') or l[0].startswith('NOTOP')]
print(len(groups),'patterns')
for p,ms in sorted(groups.items(),key=lambda x:-len(x[1])):
    H=[labs[i][0] for i,k in enumerate(p) if k=='H']; T=[labs[i][0] for i,k in enumerate(p) if k=='T']
    print(len(ms),ms[0][:2],ms[0][2]); print('    H:',H[:8]); print('    T:',T[:6])
