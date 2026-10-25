import sys
from fw import *
# B-form [t1..tn | A]: tape D(t1)..D(tn) D0 D(A) G>
def bform(ts, A):
    w=''.join(D(t) for t in ts)+D(0)+D(A)
    return w, len(w), 'G'
tests=[([1,1,4],4),([4,4],1),([1,1,1],4),([7,1],10),([6],4),([2,4],4),([0,4],4),([3,4],4),([5,4],4),([9],4),([2,1,4],1),([3,1,1],7)]
for ts,A in tests:
    w,h,q=bform(ts,A)
    out=[]
    for x in stream(M10,[('t',w,h,q)],10**7,'G0r,E0,I1,J0,J1',8):
        out.append(show(x))
    print(ts,A)
    for o in out[1:]: print('   ',o[:220])
