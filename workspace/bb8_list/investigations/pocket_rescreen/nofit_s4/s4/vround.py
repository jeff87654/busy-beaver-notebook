# vround.py MACHINE Q A B NS : 1^n <Q> -> 1^(A*n+B) <Q> (first event of shape 1+0), n in NS (python expr)
import sys
from val import run
m,Q=sys.argv[1],sys.argv[2]; A,B=int(sys.argv[3]),int(sys.argv[4]); ns=eval(sys.argv[5])
cs=[(Q,'1'*n,'','1'*(A*n+B)+'0',n) for n in ns]
ok,bad,res=run(m,Q,'R',cs,'1+0')
print('round',ok+bad,'bad',bad,[r for r in res if not r[1]][:3])
