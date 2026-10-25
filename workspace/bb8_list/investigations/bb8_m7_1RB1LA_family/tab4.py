from probe import *
import sys
pre=(5,3)
for k in range(1,8):
    row=[]
    for b in range(1,2*k+3):
        r=seq(pre+(0,)*k,0,b,1,N=10**7)[0]
        if r[0]=='K':
            d=r[1]; a=r[2]
            row.append('b%d:%s a=%s %s'%(b,'.'.join(map(str,d[2:])),a,r[3][2:]) )
        else: row.append('b%d:%s'%(b,r))
    print('k=%d'%k,' | '.join(row))
