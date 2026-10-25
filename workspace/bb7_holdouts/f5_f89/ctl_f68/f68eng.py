# f68eng.py: abstract engine for F68 = 1RB1RE_0LC0LD_1RF0LD_1LE1LB_1RA1RG_1RE---_0RC0RF (u=10, K = D on left, lead 'D00')
# state (A, L, c) same grammar as f5eng: tape = (10)^A 0 [(10)^d 0]* (10)^e 1 [(10)^c 1]; F68 run never has c>=0.
from f5eng import parse, show
def step(st):
    A,L,c=st; L=list(L)
    if c>=0: return None,'CSEG'
    if L[0]>0: L[0]-=1; return (A+2,tuple(L),c),'D'
    j=1
    while j<len(L) and L[j]==0: j+=1
    if j<len(L):                       # B_j : source s=L[j]>=1 (attached or not)
        L[:j]=[1]*(j-1)+[A+3-j]; L[j]-=1
        return (1,tuple(L),-1),'B%d'%j
    m=len(L)
    if m==1: return (1,(1,)*(A+4),-1),'T0'          # via intermediate non-template event "(A+1) #"
    j=m-1
    return (1,tuple([1]*(j-1)+[A+2-j]),-1),'T%d'%j    # length drops by one
def margin(st):
    A,L,c=st
    if L[0]>0: return None
    j=1
    while j<len(L) and L[j]==0: j+=1
    if j<len(L): return ('B',j,A+3-j)
    if len(L)==1: return ('T0',0,A+4)
    return ('T',len(L)-1,A+2-(len(L)-1))
