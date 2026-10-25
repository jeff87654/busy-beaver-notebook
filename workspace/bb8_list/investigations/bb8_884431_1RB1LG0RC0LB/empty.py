import sys
from fam import *
b=int(sys.argv[1]); N=int(sys.argv[2])
m=kstart([],0,b)
def rl(m):
    w,p=m.word()
    # run-length
    out=[];i=0
    while i<len(w):
        j=i
        while j<len(w) and w[j]==w[i]: j+=1
        out.append(w[i]+str(j-i)); i=j
    return ' '.join(out),p
nxt=10
while m.n<N:
    if not m.step(): print('HALT',m.n); break
    if m.n>=nxt:
        r=rl(m); print(m.n,ST[m.q],r[1],r[0][:200]); nxt*=3
