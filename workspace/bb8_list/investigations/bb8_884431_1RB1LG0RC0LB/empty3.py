import sys
from fam import *
b=int(sys.argv[1]); N=int(sys.argv[2])
m=kstart([],0,b)
def rl(w):
    out=[];i=0
    while i<len(w):
        j=i
        while j<len(w) and w[j]==w[i]: j+=1
        out.append(w[i]+str(j-i)); i=j
    return ' '.join(out)
last=-1
while m.n<N:
    if not m.step(): print('HALT',m.n); break
    w,p=m.word()
    if p>=len(w):
        print(m.n,ST[m.q],p,len(w),rl(w)[:150])
