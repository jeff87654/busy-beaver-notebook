import sys
from kd import *
M = CH10
def fmt(ds):
    # compress list into run notation
    out=[]; i=0; ds=list(ds)
    return ','.join(map(str,ds)) if len(ds)<60 else ','.join(map(str,ds[:30]))+'...(%d)'%len(ds)
for b in range(0, int(sys.argv[1]) if len(sys.argv)>1 else 30):
    r = run_next(M, (), 0, b, N=10**7)
    if r[0]=='K':
        print(b, r[1], 'Kd [%s] %d %d'%(fmt(r[2][0]), r[2][1], r[2][2]))
    else:
        print(b, r[:3], r[3].show()[:200] if r[0]=='HALT' else '')
