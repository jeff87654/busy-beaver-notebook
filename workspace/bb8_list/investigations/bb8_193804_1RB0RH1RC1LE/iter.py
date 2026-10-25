import sys
from fam import next_X
a=int(sys.argv[1]);cs=tuple(int(x) for x in sys.argv[2:])
n=0
while n<60:
    r=next_X(a,cs,N=10**7)
    print((a,cs),'->',r[:2] if r[0]!='X' else (r[1],r[2]))
    if r[0]!='X': break
    a,cs=r[1];n+=1
