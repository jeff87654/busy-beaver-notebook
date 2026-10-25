import sys
sys.path.insert(0,'.')
from tmlit import Sim, ST
from tr import TM
s=Sim(TM)
def rl(x):
    out=[];i=0
    while i<len(x):
        j=i
        while j<len(x) and x[j]==x[i]: j+=1
        out.append(x[i] if j-i==1 else '%s^%d'%(x[i],j-i)); i=j
    return ' '.join(out)
prev=0
for n in range(1,6400):
    q=s.state;p0=s.pos
    s.step()
    d=s.pos-p0
    if d!=prev and n<int(sys.argv[1]) :
        t=s.tape;lo,hi=s.bounds()
        L=''.join(map(str,t[lo:s.pos]));R=''.join(map(str,t[s.pos+1:hi+1]))
        print(n,rl(L),'<%s%d>'%(ST[s.state],t[s.pos]),rl(R))
    prev=d
