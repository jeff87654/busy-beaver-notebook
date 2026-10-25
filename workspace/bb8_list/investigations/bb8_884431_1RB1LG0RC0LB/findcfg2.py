import sys
from fam import *
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); n0=int(sys.argv[4]); n1=int(sys.argv[5])
m=kstart(ds,a,b)
want_left='111100'
def rle(s):
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        out.append(s[i]+'x'+str(j-i)); i=j
    return ' '.join(out)
while m.n<n1:
    if not m.step(): break
    if ST[m.q]=='F' and m.n>=n0:
        t=m.t; p=m.p
        lo=0
        while t[lo]==0: lo+=1
        left=''.join(str(t[x]) for x in range(lo,p))
        hi=len(t)-1
        while t[hi]==0: hi-=1
        right=''.join(str(t[x]) for x in range(p,hi+1))
        if left.endswith('1111') :
            print(m.n,'L:',rle(left),'| F> R:',rle(right))
