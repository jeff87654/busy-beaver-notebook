import sys
from fam import *
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); lim=int(sys.argv[4]); frm=int(sys.argv[5]) if len(sys.argv)>5 else 0
m=kstart(ds,a,b)
def line(m):
    w,p=m.word()
    # absolute window from first 1 minus 3
    lo=0
    t=m.t
    while t[lo]==0: lo+=1
    lo-=4
    hi=len(t)-1
    while t[hi]==0: hi-=1
    s=''.join(map(str,t[lo:hi+3])); pp=m.p-lo
    return s[:pp]+'['+ST[m.q]+']'+s[pp:]
while m.n<lim:
    if m.n>=frm: print(m.n,line(m))
    if not m.step(): print('HALT'); break
