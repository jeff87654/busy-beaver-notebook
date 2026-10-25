import sys
from fam import *
N=int(sys.argv[1]); show=int(sys.argv[2]) if len(sys.argv)>2 else 60
m=M(); c=0; ks=[]
while m.n<N:
    if not m.step(): print('HALT',m.n); break
    r=parse_k(m)
    if r is not None:
        c+=1
        if c<=show: print(m.n,r)
        ks.append((m.n,r))
print(len(ks), 'configs; last',ks[-1] if ks else None)
