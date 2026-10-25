# r0tab.py MACHINE Q SIDE NMAX : from (01)^n <Q> at right end, first Q-R event parsed as (01)^a 0 (01)^b ; prints compact table
import sys, re, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen'); import idle
from val import V
m,Q,side,N=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
out=subprocess.run([V,m,Q,side,'2000000000'],input=''.join(f"{Q} {'01'*n} - [01]*0\n" for n in range(1,N+1)),capture_output=True,text=True).stdout.split('\n')
res={}
for n in range(1,N+1):
    p=out[n-1].split()
    if p[0]=='H': res[n]='H'; continue
    if p[0]!='M': res[n]='?'; continue
    w='0'+p[3]; mm=re.fullmatch(r'0*((?:01)*)0((?:01)*)0',w)
    res[n]=(len(mm.group(1))//2,len(mm.group(2))//2) if mm else 'X:'+w[:30]
print(' '.join(f"{n}:{res[n] if isinstance(res[n],str) else '%d,%d'%res[n]}" for n in range(1,N+1)))
