# vlin.py MACHINE Q PRE UNIT SUF STEP N0 MOD COUNT : PRE UNIT^n SUF <Q> -> PRE UNIT^(n+STEP) SUF (first event matching shape), n=N0+MOD*j
import sys, re
from val import run
m,Q,pre,u,suf=[('' if s=='-' else s) for s in sys.argv[1:6]]; st,n0,md,cnt=map(int,sys.argv[6:10])
w=lambda n: pre+u*n+suf
rx=re.escape(pre.lstrip('0'))+'('+re.escape(u)+')*'+re.escape(suf)+'0' if pre.lstrip('0') else '[01]*'
cs=[(Q,w(n),'',(w(n+st)+'0').lstrip('0'),n) for n in range(n0,n0+md*cnt,md)]
ok,bad,res=run(m,Q,'R',cs,rx)
print('lin',ok+bad,'bad',bad,[r for r in res if not r[1]][:2])
