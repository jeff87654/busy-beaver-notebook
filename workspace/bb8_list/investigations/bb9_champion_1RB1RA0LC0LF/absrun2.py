import sys
sys.path.insert(0,'.')
from absm import tz
ds=[2,0,1,0,1,0,1,0]; a=1; b=0
it=0; lastk=None
while it<int(sys.argv[1]):
    it+=1
    if a>=1:
        b+=3*a; a=0; continue
    k=tz(ds)
    if k==len(ds):
        print('R4 at it',it,'b bits',b.bit_length(),'parity',b%2); break
    if k==0:
        ds[-1]-=1; a=b+2; b=1; continue
    if 2*k<=b:
        i=len(ds)-1-k
        print('R3 it=%d k=%d bbits=%d len=%d top=%s'%(it,k,b.bit_length(),len(ds),ds[max(0,i-3):i+1]))
        ds[i]-=1
        ds=ds[:i+1]+[b+2-2*k]+[2]*(k-1)
        a=2; b=1; continue
    print('BIG',k,b); break
