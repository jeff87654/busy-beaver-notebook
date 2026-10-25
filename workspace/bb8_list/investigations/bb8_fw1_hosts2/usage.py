import idle, random, sys
from fam import *
# slot usage by event type for each base (one event = run to next moment)
def testsB(rng):
    T=[]
    for it in range(300):
        L=rng.randint(0,5); R=[1]+[rng.choice([0,0,2,4,6]) for _ in range(L)]
        c=rng.choice([None,None,0,1,2,3,4,5,6,7,8,9,10,11]); y=2*rng.randint(2,25)+1
        if len(R)==1: y=5
        if len(R)>1 and R[-1]>=2: ev='D'
        elif len(R)==1: ev='ABS'+('o' if c is not None and c%2 else 'e' if c is not None else 'n')
        elif all(d==0 for d in R[1:]): ev='TOP'+('n' if c is None else 'c')
        else: ev='BOR'
        T.append((ev,encB(c,R,y)))
    return T
def testsA(rng):
    T=[]
    import importlib,sys
    sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\counters')
    import absA
    for it in range(300):
        L=rng.randint(0,5)
        D=[rng.choice([0,0,2,4,6,8]) for _ in range(L)]; DS=[' ']*max(0,L-1)
        if L>=1 and rng.random()<0.5:
            j=rng.randrange(L); D[j]=rng.choice([1,1,3,5,7])
        if L>=2 and rng.random()<0.3:
            j=rng.randrange(L-1); DS[j]='|'
        y=2*rng.randint(5,20)
        runs,seps=absA.canon(D+[0,y],DS+[' ',' '])
        a=absA.astep(runs,seps)
        D=runs[:-2]
        if a[0] is None: ev='X'+a[1]
        elif not D or all(d==0 for d in D): ev='EMPTY'
        elif D[-1]>=2: ev='D'
        else:
            i=len(D)-1
            while i>=0 and D[i]==0: i-=1
            ev='BOR' if D[i]>=2 else 'TOPACC'+('|' if '|' in seps else '')
            if i>0 and D[i]==1 and seps[i-1]=='|': ev='TOPACC-alt'
        T.append((ev,encA(runs,seps)))
    return T
def testsC(rng):
    T=[]
    for it in range(300):
        L=rng.randint(1,6)
        R=[rng.choice([1,3,5,7])]+[rng.choice([0,2,4,6,0,0,1,3,5]) for _ in range(L)]
        if R[-1]%2==1: R[-1]-=1
        y=2*rng.randint(L+3,L+20)+1
        if R[-1]>=2: ev='D'
        else:
            i=len(R)-1
            while i>=1 and R[i] in (0,1): i-=1
            ev='TOP' if i==0 and R[0]==1 else ('BOR' if i>0 else 'TOPx')
            if ev=='BOR' and R[i]%2: ev='BORodd'
        T.append((ev,encC(R,y)))
    return T
if __name__=='__main__':
    names=sys.argv[1:] or list(BASES)
    for nm in names:
        m,O,Q,f=BASES[nm]; rng=random.Random(1)
        T={'A':testsA,'B':testsB,'C':testsC}[f](rng)
        res=run(m,O,Q,[t[1] for t in T],10**7,1,f)
        U={}
        for (ev,_),r in zip(T,res):
            o=r[0].split()
            if o[0]=='M': s=set(re.findall('..',o[2]))
            else: s=set(); ev=ev+'/'+o[0]
            U.setdefault(ev,[0,set()]); U[ev][0]+=1; U[ev][1]|=s
        allsl=['%s%d'%(chr(65+i),c) for i in range(7) for c in range(2)]
        print(nm,m,f)
        common=set()
        for ev in U:
            if ev in ('D','BOR'): common|=U[ev][1]
        for ev in sorted(U): print('  %-12s n=%3d slots=%s  only-here=%s'%(ev,U[ev][0],' '.join(sorted(U[ev][1])),' '.join(sorted(U[ev][1]-common))))
        print('  unused by D/BOR:',' '.join(s for s in allsl if s not in common))
