# r0gen.py MACHINE Q SIDE PRE UNIT SUF NMAX [N0] : start PRE UNIT^n SUF <Q> (head on blank right of SUF, SIDE R)
# prints first Q-SIDE event as runs-compressed word (via comp)
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen'); import idle
from val import V
from comp import comp
m,Q,side,pre,u,suf,N=sys.argv[1:8]; N=int(N); n0=int(sys.argv[8]) if len(sys.argv)>8 else 1
pre='' if pre=='-' else pre; suf='' if suf=='-' else suf
ns=list(range(n0,N+1))
out=subprocess.run([V,m,Q,side,'4000000000'],input=''.join(f"{Q} {pre+u*n+suf or '-'} - [01]*0\n" for n in ns),capture_output=True,text=True).stdout.split('\n')
for n,o in zip(ns,out):
    p=o.split(); print(f"{n}:", 'H' if p[0]=='H' else (comp(p[3]).replace(' ','') if p[0]=='M' else p[0]), end='  ')
print()
