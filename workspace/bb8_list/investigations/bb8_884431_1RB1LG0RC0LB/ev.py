import sys
from fam import *
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); lim=int(sys.argv[4]); evq=sys.argv[5]
m=kstart(ds,a,b)
def rl(m):
    t=m.t; lo=0
    while t[lo]==0: lo+=1
    hi=len(t)-1
    while t[hi]==0: hi-=1
    s=''.join(map(str,t[lo-1:hi+2])); pp=m.p-(lo-1)
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        seg=s[i]+'x'+str(j-i)
        if i<=pp<j: seg='<'+ST[m.q]+'>'+seg
        out.append(seg); i=j
    return ' '.join(out)
prevq=None
while m.n<lim:
    q0=m.q
    if not m.step(): print('HALT'); break
    if ST[m.q] in evq and ST[q0] not in evq:
        print(m.n,rl(m))
