import sys
from fam import *
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
m=kstart(ds,a,b)
want_left='111100'+'111111'   # nearest first listing
while m.n<5000:
    if not m.step(): break
    if ST[m.q]=='F':
        t=m.t; p=m.p
        left=''.join(str(t[p-1-i]) for i in range(12))
        if left==want_left:
            right=''.join(map(str,t[p:p+10]))
            print(m.n,left,right)
