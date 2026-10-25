import sys
from tr import *
T1="1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE"
S1="1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF"
t1=parse(T1); t2=parse(S1)
def kword(n,b):
    D=lambda m:'10'*m+'1'
    return '11'+D(1)*(n+1)+'10'*(3*b+2)+'111001'
def m2(n,b): return '10'*(6*b+4)+'0'+'111'+'001'*(n+3)
def first_diff(word,maxs,q0=1):
    tp={}
    for i,ch in enumerate(word): tp[i]=int(ch)
    p=len(word); q=q0
    for st in range(maxs):
        c=tp.get(p,0)
        a=t1[(q,c)]; b=t2[(q,c)]
        if a!=b:
            return st,chr(65+q),c
        tp[p]=a[0]; p+=a[1]; q=a[2]
    return None
for (n,b) in [(0,0),(1,0),(0,1),(2,1)]:
    print('from M2',n,b,first_diff(m2(n,b),2000000))
for (n,b) in [(0,0),(1,0),(0,1)]:
    print('from K0',n,b,first_diff(kword(n,b),2000000))
