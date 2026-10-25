from common import *
for bp in (1,3,5,7,9,11):
    for k in range(0,12):
        r = run_next(MIR,(1,2)+(0,)*k,0,bp,N=10**6)
        print('bp',bp,'k',k, show(r[2]) if r[0]=='K' else r[:3], '' if r[0]!='K' else r[1])
