import sys
from fam import *
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); lim=int(sys.argv[4])
m=kstart(ds,a,b)
def rle(s):
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        out.append(s[i]+'x'+str(j-i)); i=j
    return ' '.join(out)
while m.n<lim:
    if not m.step(): print('HALT'); break
    if m.q==1 and m.t[m.p]==0 and not any(m.t[:m.p]):
        t=m.t; hi=len(t)-1
        while hi>m.p and t[hi]==0: hi-=1
        print(m.n,'B> ', rle(''.join(map(str,t[m.p:hi+1]))), '  K=',parse_k(m))
