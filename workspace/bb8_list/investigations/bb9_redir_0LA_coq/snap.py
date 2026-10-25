import sys
from trace0 import start
p,m,b,every=map(int,sys.argv[1:5])
s=start([9]*p+[8,0]+[1]*m+[1,3*b+1,2])
while True:
    if s.steps%every==0: print(s.steps,s.view()[:220])
    if not s.step(): print('halt',s.steps,s.view()[:220]); break
