import idle, random, sys
from pb2 import show
# Family B abstract map at a=0 moments. state: (c or None, R list of raw runs (R[0]=top=1), y odd)
def astep(c,R,y,TOP=1):
    R=list(R)
    if len(R)==1:   # ABSORB: no digits
        if y!=5: return None,'ABSY'
        if c is None: return None,'ABS-NOC'
        if c%2==0: return (None,[TOP]+[2]*(c//2+5),5)
        return (1,[TOP]+[2]*((c-1)//2+5),5)
    if R[-1]>=2 and R[-1]%2==0:
        R[-1]-=2; return (c,R,2*y+7)
    if R[-1]%2==1: return None,'LASTODD'
    n=len(R); i=n-1
    while i>=1 and R[i]==0: i-=1
    K=n-1-i
    if i==0:
        if R[0]!=TOP: return None,'TOPVAL'
        cc=(c if c is not None else -1)+y+2-2*K
        if cc<1: return None,'SMALLTOP'
        return (cc,[TOP]+[2]*(K-1),5)
    if R[i]%2==1: return None,'ODDSRC'
    v=y+3-2*K
    if v<=2: return None,'SMALL'
    R[i]-=2
    return (c,R[:i+1]+[v]+[2]*(K-1),5)
def fmt(c,R,y):
    from pb2 import comp
    s=(str(c)+'|' if c is not None else '')+' '.join(map(str,R+[0,y]))
    return comp(s)
def inp(c,R,y):
    return ('P:'+'10'*c+'1 ' if c is not None else '')+' '.join(map(str,R+[0,y]))
if __name__=='__main__':
    M,O,Q=sys.argv[1:4]; n=int(sys.argv[4]); ymax=int(sys.argv[5]) if len(sys.argv)>5 else 40
    random.seed(5); stats={}
    for it in range(n):
        L=random.randint(0,5)
        R=[1]+[random.choice([0,0,2,4,6]) for _ in range(L)]
        c=random.choice([None,None,0,1,2,3,4,5,6,7,8,9,10,11])
        y=2*random.randint(1,ymax)+1
        if len(R)==1: y=5
        a=astep(c,R,y)
        lit=show(M,O,Q,inp(c,R,y),10**8,1,4)[0]
        lit2=lit.split(' : ')[1] if ' : ' in lit else lit
        if a[0] is None and len(a)==2:
            key=(a[1],'H' if lit.startswith('H') else 'K')
            if lit.startswith('H'): print('HALT',fmt(c,R,y),a[1])
        else:
            exp=fmt(*a)
            ok=(exp==lit2)
            key=('OK' if ok else 'MISMATCH',)
            if not ok: print('MISMATCH',fmt(c,R,y),'exp',exp,'lit',lit)
        stats[key]=stats.get(key,0)+1
    print(stats)
