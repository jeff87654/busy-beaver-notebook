import sys
from rulecheck import *
def rle(w):
    out=[]; i=0
    while i<len(w):
        j=i
        while j<len(w) and w[j]==w[i]: j+=1
        out.append(w[i]+('^%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(out)
for n in range(0,4):
  for b in range(0,4):
    s = sim_from([0]*n, 0, b)
    found = []
    while s.steps < 3000:
        if s.pos == s.lo and ST[s.state]=='A' and s.tape[s.pos]==1:
            found.append((s.steps, rle(''.join(map(str,s.tape[s.lo:s.hi+1])))))
            break
        if not s.step(): break
    print(n,b,found)
