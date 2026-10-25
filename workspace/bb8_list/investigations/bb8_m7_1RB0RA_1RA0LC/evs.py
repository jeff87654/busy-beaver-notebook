from seqk import *
import sys
n=int(sys.argv[1]); N=int(sys.argv[2])
for b in [int(x) for x in sys.argv[3].split(',')]:
    prev=None; evs=[]
    for x in kseqS(n,b,N):
        if isinstance(x,str): continue
        st,t,r=x
        if prev is not None and isR1(prev[0],prev[1],t,r): prev=(t,r); continue
        evs.append((st,rl(t),r)); prev=(t,r)
    print('n=%d b=%d'%(n,b), ' | '.join('%d %s r=%d'%e for e in evs[:3]),flush=True)
