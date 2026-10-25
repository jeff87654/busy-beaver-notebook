# vgrid.py MACHINE Q SIDE PRE X MID Y SUF DA DB AMIN BMIN : config PRE X^a MID Y^b SUF <Q> at SIDE R; expect next event PRE X^(a+DA) MID Y^(b+DB) SUF
import sys
from val import run
m,Q,side,pre,X,mid,Y,suf=[('' if s=='-' else s) for s in sys.argv[1:9]]; da,db,amin,bmin=map(int,sys.argv[9:13])
def word(a,b): return pre+X*a+mid+Y*b+suf
cs=[(Q,word(a,b),'',(word(a+da,b+db)+'0').lstrip('0'),(a,b)) for a in range(amin,amin+12) for b in range(bmin,bmin+12)]
ok,bad,res=run(m,Q,side,cs,'[01]*0')
print('grid',ok+bad,'bad',bad,[r for r in res if not r[1]][:3])
