from probe import *
import sys
for k in range(1,9):
    row=[]
    for b in range(1,13):
        r=seq((1,2)+(0,)*k,0,b,1,N=10**7)[0]
        row.append(str(r[1][2:]) if r[0]=='K' else str(r))
    print('k=%d'%k,' '.join(row))
