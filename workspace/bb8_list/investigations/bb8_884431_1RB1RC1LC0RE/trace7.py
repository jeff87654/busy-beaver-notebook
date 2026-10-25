import sys
from rulecheck import *
def rle(w):
    out=[]; i=0
    while i<len(w):
        j=i
        while j<len(w) and w[j]==w[i]: j+=1
        out.append(w[i]+('^%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(out)
k=int(sys.argv[1]); y=int(sys.argv[2]); b=int(sys.argv[3]); lim=int(sys.argv[4])
L=[0]*(k+1)+[y+1]
s = sim_from(L[::-1], 0, b)
last=None
while s.steps < lim:
    if s.pos == s.lo and ST[s.state] in 'AE' :
        w=''.join(map(str,s.tape[s.lo:s.hi+1]))
        key=(ST[s.state], w[:1])
        print(s.steps, ST[s.state], rle(w))
    if not s.step(): break
