import sys, itertools
from cyc import *
from enum1 import cycle
blocks=['00','01','10','11']
n=int(sys.argv[1]); L=int(sys.argv[2]); tail=sys.argv[3]
for combo in itertools.product(blocks,repeat=L):
    pre=''.join(combo)
    Rs=pre+parse_blocks(tail)+'0'*40
    kind,k,res,reach=cycle(n,Rs)
    if kind!='stop': print(' '.join(combo),kind,k,'reach',reach); continue
    Lr,Rr,pos=res
    if len(Lr)%2: Lr='0'+Lr
    if len(Rr)%2: Rr+='0'
    print(' '.join(combo),'|',tail,'->',k,bl(Lr)[:60],'[A]',bl(Rr)[:100],'reach',reach)
