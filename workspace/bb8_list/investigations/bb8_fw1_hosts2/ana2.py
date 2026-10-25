import idle, sys, collections
from ana import load, kind
from fam import BASES
nm=sys.argv[1]; mode=sys.argv[2]; f=BASES[nm][3]
labs,V=load(nm,mode)
g=collections.defaultdict(list)
for m,outs in V:
    ks=''.join(kind(o,f) for o in outs)
    if set(ks)<={'=','H'}: g[ks].append(m)
for ks,ms in sorted(g.items(),key=lambda x:-len(x[1])):
    hl=[labs[i][0] for i,k in enumerate(ks) if k=='H']
    print(len(ms),ms[0],'\n    HALTS:',len(hl),'/',len(ks),'; '.join(hl[:12]),'...' if len(hl)>12 else '')
