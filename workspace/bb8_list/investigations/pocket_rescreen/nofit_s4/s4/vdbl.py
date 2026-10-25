# doubling rule validator for the F4 '(01)^n at B' family. usage: vdbl.py MACHINE Q SIDE
from val import run
import sys
m, Q, side = sys.argv[1], sys.argv[2], sys.argv[3]
def w(a,b): return ('01'*a+'0'+'01'*b+'0').lstrip('0')
def r0(n):
    k=1
    while 2**(k+1)-1<=n: k+=1      # 2^k-1 <= n < 2^(k+1)-1
    if n==2**(k+1)-2: return 'H'
    return w(2**(k+1)-3-n, 2*n-2**(k+1)+5)
c0=[(Q,'01'*n,'',None,n) for n in range(1,301)]
ok,bad,res=run(m,Q,side,c0,'[01]*0')
b0=[]
for (tag,g,o),n in zip(res,range(1,301)):
    pass
out=__import__('subprocess').run([__import__('val').V,m,Q,side,'1000000000'],input=''.join(f"{Q} {'01'*n} - [01]*0\n" for n in range(1,301)),capture_output=True,text=True).stdout.split('\n')
bad0=[]
for n in range(1,301):
    p=out[n-1].split(); e=r0(n)
    got='H' if p[0]=='H' else (p[3] if p[0]=='M' else '?')
    if got!=e: bad0.append((n,out[n-1][:60]))
print('R0 cases 300 bad',len(bad0),bad0[:4])
c1=[(Q,('01'*a+'0'+'01'*b),'',w(a-1,b+2),(a,b)) for a in range(1,13) for b in range(1,26)]
ok,bad,res=run(m,Q,side,c1,'[01]*0')
print('R1 cases',ok+bad,'bad',bad,[r for r in res if not r[1]][:4])
