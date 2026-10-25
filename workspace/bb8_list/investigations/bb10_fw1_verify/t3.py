import sys
from fw import *
n,b,ev,mx,steps=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3],int(sys.argv[4]),int(float(sys.argv[5]))
mach = M10 if len(sys.argv)<7 else REC8
w,h,q=K(n,b)
for x in stream(mach,[("n%db%d"%(n,b),w,h,q)],steps,ev,mx):
    print(show(x),flush=True)
