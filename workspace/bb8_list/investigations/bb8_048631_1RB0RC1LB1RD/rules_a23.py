import itertools,sys
from randlist import run
BIG=(40,)
out={}
def succ(a,ts):
    r=run(a,ts,10000000)
    assert r[0]=='std',(a,ts,r)
    return r[1]
def diff(ts,res):
    # strip common suffix
    t1=list(ts); t2=list(res)
    i=0
    while i<min(len(t1),len(t2)) and t1[len(t1)-1-i]==t2[len(t2)-1-i]: i+=1
    return tuple(t1[:len(t1)-i]),tuple(t2[:len(t2)-i])
for a in (2,3):
    print('== a =',a)
    seen={}
    for L in range(0,5):
        for X in itertools.product(range(1,7),repeat=L):
            ts=X+BIG
            a2,r=succ(a,ts)
            p1,p2=diff(ts,r)
            seen[X]=(a2,p1,p2)
    # print minimal patterns: show (X)->(a2,p1->p2) for L<=3 
    for X in sorted(seen,key=lambda x:(len(x),x)):
        if len(X)<=3: print(X,'->',seen[X])
