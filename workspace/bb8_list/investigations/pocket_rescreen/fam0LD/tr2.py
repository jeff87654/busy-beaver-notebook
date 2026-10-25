import sys
from sim import parse
from dec import dec
def rl(xs):
    out=[];i=0
    while i<len(xs):
        j=i
        while j<len(xs) and xs[j]==xs[i]: j+=1
        out.append(str(xs[i])+('^%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(out) or '-'
m=sys.argv[1]; N=int(sys.argv[2]); T=parse(m)
tape=bytearray(1<<22); pos=1<<21; st=0; hi=pos; prev=None
for n in range(N):
    c=tape[pos]
    if (st,c) not in T: print('HALT',n); break
    w,d,q=T[(st,c)]; tape[pos]=w
    if w and pos>hi: hi=pos
    pos+=d; st=q
    if st==6 and tape[pos]==0 and tape[pos-1]==0 and tape[pos-2]==0:
        # assume nothing left (check small window)
        s=bytes(tape[pos+1:hi+1]).decode('latin1').translate({0:48,1:49}) if False else ''.join('1' if x else '0' for x in tape[pos+1:hi+1])
        r=dec(s.rstrip('0'))
        if r is None: continue
        ds,a,b=r
        if prev and not (prev[0]==ds and a==prev[1]-1 and b==prev[2]+2):
            print(n+1,'|',rl(prev[0]),prev[1],prev[2],'->',rl(ds),a,b)
        prev=(ds,a,b)
