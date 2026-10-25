import idle,sys
from rules import *
from fractions import Fraction
M = M1 if sys.argv[1]=='1' else M2
def fitpoly(xs,ys,deg=2):
    # exact lagrange-based check: fit on first deg+1 points, test rest
    import numpy as np
    from fractions import Fraction as F
    n=deg+1; X=xs[:n]; Y=ys[:n]
    # solve vandermonde exactly
    A=[[F(x)**p for p in range(n)] for x in X]; b=[F(y) for y in Y]
    for i in range(n):
        piv=A[i][i]
        for j in range(i+1,n):
            f=A[j][i]/piv
            A[j]=[A[j][t]-f*A[i][t] for t in range(n)]; b[j]-=f*b[i]
    c=[0]*n
    for i in reversed(range(n)):
        c[i]=(b[i]-sum(A[i][t]*c[t] for t in range(i+1,n)))/A[i][i]
    ok=all(sum(c[p]*x**p for p in range(n))==y for x,y in zip(xs,ys))
    return c,ok
# D steps vs a (and independence from d, rest)
for ds in ([1],[5,2,0,3],[2,0,0]):
    xs=list(range(1,15)); ys=[nextk(M,a,ds)[1] for a in xs]
    print('D',ds,fitpoly(xs,ys))
for k in range(1,8):
    for tail in ([1],[3,0,2]):
        xs=list(range(max(1,(k+2)//3),20)); ys=[nextk(M,a,[0]*k+tail)[1] for a in xs]
        print('B',k,tail,fitpoly(xs,ys))
for k in range(1,8):
    xs=list(range(max(1,(k+2)//3),20)); res=[nextk(M,a,[0]*k) for a in xs]
    print('E',k,'steps',fitpoly(xs,[r[1] for r in res]),'ones',fitpoly(xs,[r[2] for r in res]))
