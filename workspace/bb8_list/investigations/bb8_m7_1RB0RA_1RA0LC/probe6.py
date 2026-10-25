from batch import *
import itertools, sys
alpha=[0,1,2,3,4,7]
a_vals=[int(x) for x in sys.argv[1].split(',')]
L=int(sys.argv[2])
cfgs=[]
for t in itertools.product(alpha,repeat=L):
    for a in a_vals:
        for r in (2,5):
            cfgs.append((list(t)+[a],r))
res=run(cfgs,tail='111001',N=20000000)
def short(l):
    if len(l)>14: return str(l[:6])+'..(%d)..'%len(l)+str(l[-4:])
    return str(l)
for t,r,x in res:
    print(t,r,'->',(x[1] if len(x[1])<=14 else short(x[1]), x[2], 'steps',x[0]) if isinstance(x,tuple) else x)
