import sys
from fhlit import *
b=int(sys.argv[1]); nz=int(sys.argv[2]) if len(sys.argv)>2 else 35
s=start([1]*nz+[1,3*b])
ev=0
while s.steps<5*10**7:
    q=s.q; c=s.t[s.pos]
    if (q,c) in (('E',0),('I',1),('I',0)):
        print(s.steps,q,c,s.view()[:220]); ev+=1
    if ev>0:
        t=parse(s)
        if t is not None:
            print('FAM',s.steps,s.view()[:220])
            if 37 in t: break
    if not s.step(): print('halt',s.q,s.steps); break
