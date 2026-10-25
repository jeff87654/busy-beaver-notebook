import sys
from fam import *
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
m=kstart(ds,a,b)
lo=m.p
def line(m):
    s=''.join(map(str,m.t[lo-2:lo+60]))
    p=m.p-(lo-2)
    return s[:p]+'['+ST[m.q]+']'+s[p:]
prevq=None
print(m.n,line(m))
while True:
    if not m.step(): print('HALT'); break
    print(m.n,line(m))
    if m.n>=int(sys.argv[4]): break
    if parse_k(m): print('--K',parse_k(m)); break
