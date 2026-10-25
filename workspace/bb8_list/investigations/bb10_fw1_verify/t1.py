from fw import *
for n in [3,5]:
  for b in [0,1,2]:
    w,h,q=K(n,b)
    r=run(M10,[('n%db%d'%(n,b),w,h,q)],10**9,'E0,I1,J0,J1',12)
    for x in r:
        if x['kind']=='EV':
            it,idx,off=tokpos(x['word'],x['rel'])
            print(x['lab'],x['n'],x['step'],x['q'],x['c'],'head@tok',idx,off,'|',fmt(it[:idx]),'[[',fmt(it[idx:idx+1]),']]',fmt(it[idx+1:]))
        else: print(x)
