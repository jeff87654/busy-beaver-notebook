from probe import *
import sys
pre=(7,)
y1=int(sys.argv[1]) if len(sys.argv)>1 else 3
for k in range(1,8):
    print('k=%d'%k)
    for b in range(1,k+4):
        r=seq(pre+(y1,)+(0,)*k,0,b,1,N=10**7)[0]
        if r[0]=='K':
            d=r[1]; a=r[2]
            print('   b=%d: %s  a=%s b=%s steps%s'%(b,'.'.join(map(str,d)),a,r[3][2:],r[4]))
        else: print('   b=%d: %s'%(b,r))
