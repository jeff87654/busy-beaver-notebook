import sys
from symchk import first_p1, norm, show, symnames, Lin
H=('H',1); H2=('H',1,2)
def X(i): return Lin({'X%d'%i:1})
def build(digs):
    """digs with symbols -> (input digs, value env list: Lin per digit, Z marks)"""
    nm=symnames(digs); vals=[]
    for i,e in enumerate(digs):
        if isinstance(e,int): vals.append(Lin.c(e))
        elif e[0]=='H': vals.append(Lin({nm[i]:1})+(e[2] if len(e)>2 else 0))
        else: vals.append(('Z',Lin({nm[i]:1})))
    return vals
def flat(v):
    out=[]
    for e in v:
        if isinstance(e,tuple) and e[1].isconst(): out+=[Lin.c(1)]*int(e[1].const())
        else: out.append(e)
    return out
def canon(v):
    out=[]
    for e in v:
        if isinstance(e,tuple) or (isinstance(e,Lin) and e==Lin.c(1)):
            n=e[1] if isinstance(e,tuple) else Lin.c(1)
            if out and isinstance(out[-1],tuple): out[-1]=('Z',out[-1][1]+n)
            else: out.append(('Z',n))
        else: out.append(e)
    return out
def eq(a,b):
    a=canon(a); b=canon(b)
    if len(a)!=len(b): return False
    for x,y in zip(a,b):
        if isinstance(x,tuple)!=isinstance(y,tuple): return False
        if isinstance(x,tuple):
            if not (x[1]==y[1]): return False
        elif not (x==y): return False
    return True
tests=[]
rests=[[],[H],[H,H],[1],[1,H],[H2,1],[3],[1,1,H]]
for r in rests: tests.append(('D',[H,H2]+r, lambda v: [v[0]+4, v[1]-2]+v[2:]))
for k in list(range(1,21)):
    for r in rests[:6]:
        tests.append(('B%d'%k,[H]+[1]*k+[H2]+r, lambda v,k=k: [Lin.c(1)]*k+[v[0]+4, v[k+1]-2]+v[k+2:]))
for r in rests[:6]:
    for zr in (0,1):
        tests.append(('Bz',[H,1,('Z',zr),H2]+r, lambda v: [Lin.c(1),('Z',v[2][1]),v[0]+4,v[3]-2]+v[4:]))
for k in range(1,21):
    tests.append(('T%d'%k,[H]+[1]*k, lambda v,k=k: [v[0]+4] if k==1 else [Lin.c(1)]*(k-1)+[v[0]+4]))
for zr in (0,1):
    tests.append(('Tz',[H,1,('Z',zr),1], lambda v: [Lin.c(1),('Z',v[2][1]),v[0]+4]))
    tests.append(('Tz2',[H,('Z',zr),1], lambda v: [('Z',v[1][1]),v[0]+4]))
tests.append(('S',[H], lambda v: [('Z',v[0][1] if False else v[0]+2)] ))
tests.append(('S',[H2], lambda v: [('Z',v[0]+2)] ))
bad=0; cnt=0
for name,digs,f in tests:
    vals=build(digs); exp=f(vals)
    got,verd=first_p1(digs)
    cnt+=1
    ok = got is not None and eq(got,exp)
    if not ok:
        bad+=1; print('FAIL',name,digs,'got',show(got) if got else verd,'exp',show(exp))
print('symbolic tests',cnt,'fail',bad)
