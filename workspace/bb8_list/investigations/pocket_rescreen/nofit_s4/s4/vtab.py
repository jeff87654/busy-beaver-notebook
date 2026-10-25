# vtab.py MACHINE Q SIDE KIND NMAX : check R0 table formula (KIND) for n=1..NMAX and R1 grid (a,b)->(a-1,b+2)
import sys, re, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen'); import idle
from val import V, run
m,Q,side,kind,N=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5])
def w(a,b): return ('01'*a+'0'+'01'*b+'0').lstrip('0')
def plain(n): return ('01'*n+'0').lstrip('0')
def f_c1(n):
    k=1
    while 2**(k+1)-1<=n: k+=1
    if n==2**(k+1)-2: return 'H'
    return w(2**(k+1)-3-n, 2*n-2**(k+1)+5)
def f_c3(n):  # base 3*2^k-2
    if n==1: return w(1,2)
    k=0
    while 3*2**(k+1)-2<=n: k+=1
    m=3*2**k-2
    if n==3*2**(k+1)-4: return plain(n+2)
    if n==3*2**(k+1)-3: return 'H'
    return w(2*m-n, 2*(n-m)+2)
F={'c1':f_c1,'c3':f_c3}[kind]
out=subprocess.run([V,m,Q,side,'2000000000'],input=''.join(f"{Q} {'01'*n} - [01]*0\n" for n in range(1,N+1)),capture_output=True,text=True).stdout.split('\n')
bad=[]
for n in range(1,N+1):
    p=out[n-1].split(); got='H' if p[0]=='H' else (p[3] if p[0]=='M' else '?')
    if got!=F(n): bad.append((n,out[n-1][:50]))
c1=[(Q,('01'*a+'0'+'01'*b),'',w(a-1,b+2),(a,b)) for a in range(1,13) for b in range(1,26)]
ok,b1,res=run(m,Q,side,c1,'[01]*0')
print(f'R0 {N} bad {len(bad)} {bad[:3]} R1 {ok+b1} bad {b1} {[r for r in res if not r[1]][:3]}')
