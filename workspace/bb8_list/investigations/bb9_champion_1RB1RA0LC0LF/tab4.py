import sys
sys.argv=[sys.argv[0],'40']
from modeval import *
P=int(sys.argv[1]) if False else 3
import itertools
for j in range(0,10):
    out={}
    for xr in range(0,8):          # x mod 8
        for vr in range(0,4):      # v mod 4 (huge v) 
            x=Huge(xr+8*1000003,64)   # huge with residue
            # make huge: Huge flags huge
            v=Huge(vr+4*(1<<30),64)
            if vr==0 and False: continue
            try:
                r=CD(j,v,x)
            except Exception as e:
                out[(xr,vr)]='ERR'; continue
            out[(xr,vr)]=low(r,P)
    # print table rows by x mod 8: for v parity classes
    print('depth',j)
    for xr in range(8):
        print('  x%%8=%d: '%xr+' '.join('v%%4=%d->%s'%(vr,out[(xr,vr)]) for vr in range(4)))
