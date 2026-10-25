# f5eng.py: abstract engine for the F5 family (u=10 coding, K = M1 D-left / M2 E-left / M3 G-right)
# state (A, L, c): tape = (10)^A 0 [ (10)^L[0] 0 ... (10)^L[-2] 0 ] (10)^L[-1] 1 [ (10)^c 1 if c>=0 ]
import re
def parse(line):
    toks=[]
    for t in line.split():
        m=re.match(r'\((\d+) \.\)\^(\d+)$',t)
        toks.append(t)
    s=' '.join(toks)
    # expand (x .)^r
    s=re.sub(r'\((\d+) \.\)\^(\d+)', lambda m: ' '.join([m.group(1)+' .']*int(m.group(2))), s)
    t=s.split()
    if not t or not t[0].isdigit(): return None
    A=int(t[0]); i=1
    if i>=len(t) or t[i]!='.': return None
    i+=1; L=[]; c=-1
    while True:
        v=0
        if i<len(t) and t[i].isdigit(): v=int(t[i]); i+=1
        if i>=len(t): return None
        sep=t[i]; i+=1; L.append(v)
        if sep=='#': break
        if sep!='.': return None
    if i<len(t):
        if not t[i].isdigit(): return None
        c=int(t[i]); i+=1
        if i!=len(t)-1 or t[i]!='#': return None
    return (A,tuple(L),c)
def step(st):
    A,L,c=st; L=list(L)
    if L[0]>0: L[0]-=1; return (A+2,tuple(L),c),'D'
    i=1
    while i<len(L)-1 and L[i]==0: i+=1
    if len(L)==1: i=0
    j=i
    if i<len(L)-1 or (i==len(L)-1 and L[i]>=2):
        s=L[i]
        if s<2: return None,'ODD-SOURCE'
        new=[2]*(j-1)+[A+4-2*j]; L[:j]=new; L[j]-=2
        return (2,tuple(L),c),'B%d'%j
    e=L[-1]
    if e==1:
        if j==0: return None,'?'
        return (2,tuple([2]*(j-1)+[A+c+4-2*j]),-1),'M%d'%j
    # e==0 : top
    if j==0:
        if (A+c+3)%2: return None,'T0-ODD'
        return (2,tuple([2]*((A+c+3)//2)+[0]),-1),'T0'
    return (2,tuple([2]*(j-1)+[1]),A+c+2-2*j),'T%d'%j
def show(st):
    A,L,c=st
    out=[];i=0
    while i<len(L):
        k=i
        while k<len(L) and L[k]==L[i]: k+=1
        out.append(str(L[i])+('^%d'%(k-i) if k-i>1 else '')); i=k
    return '[%d | %s%s]'%(A,' '.join(out),(' | c=%d'%c) if c>=0 else '')
def margin(st):
    """value created by the next non-D rule (the quantity that must stay above a small threshold); None for D"""
    A,L,c=st
    if L[0]>0: return None
    i=1
    while i<len(L)-1 and L[i]==0: i+=1
    if len(L)==1: i=0
    j=i
    if i<len(L)-1 or L[i]>=2: return ('B',j,A+4-2*j)
    if L[-1]==1: return ('M',j,A+c+4-2*j)
    if j==0: return ('T0',0,A+c+3)
    return ('T',j,A+c+2-2*j)
