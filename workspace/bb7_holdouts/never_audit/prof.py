import sys, time, idle_guard
sys.argv=sys.argv[:1]
import audit2
from fam import *
from coding import U10Coding
C=U10Coding(); m=mirror('1RB1RG_1LC1LF_1RE0LD_1LB1RC_---0LB_0RA0RC_1RA1RF')
for v0,prove in [(['H3','H0'],True),(['H3',0,'H0'],True),(['H3',0,0,0,'H0'],True),(['H3',0,0,0,0,0,0,'H0'],True),(['H5'],True)]:
    tp=C.encode(v0,[2],0,'C')
    for NS in (3,12,48):
        t=time.time(); v,st,fin,raw=run_sym(m,'C',tp,stopn=NS,mg=720,hlb=1000,budget=300000,tlimit=30,prove=prove)
        ds=[]
        for a,tt,sd in st:
            try:
                q,vv,zz,rb=stop_v(tt); d,tf=C.decode(vv,1); ds.append((zz,vshow(d),tf))
            except Exception as e: ds.append(('ERR',str(e)[:40]))
        print(v0,NS,v,'%.1fs'%(time.time()-t),ds[:4])
