import idle, sys, collections, re
from ana import load, kind
from fam import BASES, dec
KEYS={'C':['TOP t=1 B=[0] y=59','TOP t=1 B=[1, 0] y=123','TOP t=3 B=[0] y=59','NOTOP B=[1, 0] y=59'],
      'B':['TOP c=6 K=2 y=57','TOP c=None K=1 y=17','ABS c=16','ABS c=31','NOTOP c=16 K=2 y=57']}
def sh(o,f):
    if o[0]!='M': return o[0]
    return dec(f,o[1:])
if __name__=='__main__':
    names=sys.argv[2:]; mode=sys.argv[1]
    for nm in names:
        f=BASES[nm][3]; labs,V=load(nm,mode); L=[l[0] for l in labs]
        idx=[L.index(k) for k in KEYS[f]]
        g=collections.defaultdict(list)
        for m,outs in V:
            g[tuple(sh(outs[i],f) if outs[i]!='=' else '=' for i in idx)].append(m)
        print('==',nm,'base:',' || '.join(labs[i][1] for i in idx))
        for k,ms in sorted(g.items(),key=lambda x:-len(x[1])):
            print('%4d %-60s %s'%(len(ms),ms[0],' || '.join(x[:40] for x in k)))
