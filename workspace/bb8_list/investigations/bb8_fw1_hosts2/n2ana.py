import idle, collections, sys, re
from ana import load
from n2c import dec
def kind(o): return '=' if o=='=' else ('H' if o[0]=='H' else ('M' if o[0]=='M' else 'T'))
def shape(o):
    if o=='=': return '='
    if o[0]!='M': return o[0]
    s=dec(o[1:]); return re.sub(r'(1,1;)+','(1,1)*;',s)
for mode in sys.argv[1:]:
    labs,V=load('N2',mode)
    c=collections.Counter(); g=collections.defaultdict(list)
    L=[l[0] for l in labs]
    keys=[L.index('x0 y=17'),L.index('x0 y=31'),L.index('11^2 1,9'),L.index('1,17')]
    for m,outs in V:
        ks=''.join(kind(o) for o in outs); s=''.join(sorted(set(ks)-{'='}))
        if s=='H':
            allh=all(k=='H' for k in ks if True)
            s='H-all' if all(ks[i]=='H' for i in range(len(ks))) else 'H-partial'
        c[s]+=1
        g[(s,tuple(shape(outs[i])[:60] for i in keys))].append(m)
    print('N2',mode,dict(c))
    for k,ms in sorted(g.items(),key=lambda x:-len(x[1]))[:int(sys.argv[-1]) if sys.argv[-1].isdigit() else 25]:
        print('%4d %-10s %s'%(len(ms),k[0],ms[0])); print('        ',' || '.join(k[1]))
