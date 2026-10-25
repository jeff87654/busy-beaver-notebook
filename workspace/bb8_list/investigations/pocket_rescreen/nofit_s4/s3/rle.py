# rle.py M N Q side K : events (Q at extreme side); print run-length encoding of tape when first long run <= K (or K<0: all)
import sys,subprocess,re,itertools
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
from val import expand
M,N,Q,S,K=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5])
p=subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s3\sim.exe',M,N,'at',Q,S,'100000000'],stdout=subprocess.PIPE,text=True)
for ln in p.stdout:
    m=re.match(r'(\d+) (\w) \| (.*) <\w> (.*)$',ln.strip())
    if not m: print(ln.strip()); continue
    L=expand(m.group(3)); R=expand(m.group(4)); t=L+'|'+R
    runs=[(k,len(list(g))) for k,g in itertools.groupby(t)]
    s=' '.join(k if n==1 else '%s^%d'%(k,n) for k,n in runs)
    big=[n for k,n in runs if n>3]
    if K<0 or (big and big[0]<=K): print(m.group(1),s[:200])
