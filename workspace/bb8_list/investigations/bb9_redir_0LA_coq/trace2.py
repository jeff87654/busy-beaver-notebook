import sys
from trace0 import start
p,m,b=map(int,sys.argv[1:4]); lim=int(sys.argv[4]) if len(sys.argv)>4 else 400
s=start([9]*p+[8,0]+[1]*m+[1,3*b+1,2])
n=0
while s.steps<10**8:
    q=s.q; c=s.t[s.pos]
    if q in 'EI' and (q,c)!=('E',1):
        print(s.steps,q,c,s.view()[:300])
    if q=='G' and c==0 and s.t.rfind(1)<s.pos:
        print('FAM',s.steps,s.view()[:300]); n+=1
        if n>lim: break
    if not s.step(): print('halt',s.q,s.t[s.pos],s.steps,s.view()[:300]); break
