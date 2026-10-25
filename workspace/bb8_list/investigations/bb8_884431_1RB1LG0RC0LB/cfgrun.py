import sys
from sim8 import *
def rle(s):
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        out.append(s[i]+'x'+str(j-i)); i=j
    return ' '.join(out)
# usage: cfgrun.py leftword state rightword steps   (words as bit strings; leftword leftmost first)
lw,q,rw,N=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
m=M(lw+rw,len(lw),q)
def show(m):
    t=m.t
    lo=0
    while t[lo]==0: lo+=1
    hi=len(t)-1
    while t[hi]==0: hi-=1
    s=''.join(map(str,t[min(lo,m.p):max(hi,m.p)+1]))
    base=min(lo,m.p)
    return rle(s[:m.p-base])+' ['+ST[m.q]+'] '+rle(s[m.p-base:])
print(0,show(m))
step=int(sys.argv[5]) if len(sys.argv)>5 else 1
while m.n<N:
    if not m.step(): print('HALT'); break
    if m.n%step==0: print(m.n,show(m))
