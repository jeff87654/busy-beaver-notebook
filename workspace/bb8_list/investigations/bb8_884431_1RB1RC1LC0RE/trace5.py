import sys, re
from rulecheck import *
n=int(sys.argv[1]); b=int(sys.argv[2]); lim=int(sys.argv[3])
s = sim_from([0]*n, 0, b)
def rle(w):
    out=[]; i=0
    while i<len(w):
        j=i
        while j<len(w) and w[j]==w[i]: j+=1
        out.append(w[i]+('^%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(out)
def disp(s):
    lo, hi = s.bounds()
    t = s.tape
    L=''.join(map(str,t[lo:s.pos])); R=''.join(map(str,t[s.pos+1:hi+1]))
    return '%s [%s%d] %s' % (L, ST[s.state], t[s.pos], R)
cnt=0
last_state=None
while s.steps < lim:
    if s.pos == s.lo or s.pos == s.hi:
        # head at an end of the nonblank part
        k = (ST[s.state], s.pos==s.lo)
        if k != last_state:
            print(s.steps, ST[s.state], 'LEFT' if s.pos==s.lo else 'RIGHT', rle(''.join(map(str,s.tape[s.lo:s.hi+1]))))
        last_state = k
    else: last_state=None
    if not s.step(): break
