# blocks.py M N Q : run sim rec, keep Q-left events, print block lengths (split on 0) only when the first block is small (<=K)
import sys,subprocess,re
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
from val import expand
M,N,Q,K=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
p=subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s3\sim.exe',M,N,'at',Q,sys.argv[5] if len(sys.argv)>5 else 'L','10000000'],stdout=subprocess.PIPE,text=True)
for ln in p.stdout:
    m=re.match(r'(\d+) (\w) \| (.*) <\w> (.*)$',ln.strip())
    if not m: print(ln.strip()); continue
    t=expand(m.group(3))+expand(m.group(4))
    t=t.strip('0') if True else t
    b=[len(x) for x in t.split('0')]
    lead=len(expand(m.group(4)))-len(expand(m.group(4)).lstrip('0'))
    if min(b[:1])<=K or len(b)<=1: print(m.group(1),lead,b if len(b)<12 else str(b[:6])+'..'+str(b[-4:])+' n=%d'%len(b))
