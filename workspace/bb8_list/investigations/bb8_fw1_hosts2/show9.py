import idle, sys
from ana import load
from fam import dec
nm,mode,m=sys.argv[1:4]
labs,V=load(nm,mode); d=dict(V); outs=d[m]
for i,o in enumerate(outs):
    if labs[i][0].startswith('TOP t=1') or labs[i][0].startswith('NOTOP'):
        print('   %-26s %-40s base %s'%(labs[i][0], (dec('C',o[1:]) if o[0]=='M' else o)[:40], labs[i][1][:34]))
