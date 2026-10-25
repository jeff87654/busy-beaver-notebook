import idle, sys
from ana import load, kind
from fam import BASES, dec
nm,mode=sys.argv[1:3]; f=BASES[nm][3]; labs,V=load(nm,mode)
for m,outs in V:
    ks=''.join(kind(o,f) for o in outs); s=set(ks)-{'='}
    if len(s)>=2 or (len(sys.argv)>3 and sys.argv[3] in s and len(s)==1):
        print(m)
        for i,o in enumerate(outs):
            if o!='=': print('    %-30s %s   [base %s]'%(labs[i][0], dec(f,o[1:])[:60] if o[0]=='M' else o, labs[i][1][:40]))
