import idle, sys, collections
from ana import load, kind
from fam import BASES, dec
nm=sys.argv[1]; mode=sys.argv[2]; f=BASES[nm][3]; cls=sys.argv[3] if len(sys.argv)>3 else 'M'
show=int(sys.argv[4]) if len(sys.argv)>4 else 6
labs,V=load(nm,mode)
g=collections.defaultdict(list)
for m,outs in V:
    ks=''.join(kind(o,f) for o in outs)
    if cls in ks: g[tuple(o if o[0]!='M' else 'M'+dec(f,o[1:]) for o in outs)].append(m)
print(len(g),'distinct outcome vectors')
for key,ms in sorted(g.items(),key=lambda x:-len(x[1]))[:show]:
    print(len(ms),ms[:3])
    for i,o in enumerate(key):
        if o!='=': print('     %-28s -> %s   [base %s]'%(labs[i][0],o[:90],labs[i][1][:50]))
