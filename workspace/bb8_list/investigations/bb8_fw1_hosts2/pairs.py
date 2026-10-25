import idle, random, sys, os, re
os.environ['EVPAIRS']='1'
from fam import *
from usage import testsA, testsB, testsC
def pairs_of(mask):
    a,b=mask.split(':'); return set(re.findall('...',b))
if __name__=='__main__':
    names=sys.argv[1:] or list(BASES)
    for nm in names:
        m,O,Q,f=BASES[nm]; rng=random.Random(1)
        T={'A':testsA,'B':testsB,'C':testsC}[f](rng)
        T+= {'A':testsA,'B':testsB,'C':testsC}[f](random.Random(2))
        res=run(m,O,Q,[fixtape(nm,t[1]) for t in T],10**7,1,filt(nm))
        U={}
        for (ev,_),r in zip(T,res):
            o=r[0].split()
            if o[0]=='M': s=pairs_of(o[2])
            else: s=set(); ev=ev+'/'+o[0]
            U.setdefault(ev,[0,set()]); U[ev][0]+=1; U[ev][1]|=s
        common=set()
        for ev in U:
            if ev in ('D','BOR','BORodd'): common|=U[ev][1]
        print(nm,m,O,Q,f,' engine pairs:',len(common))
        for ev in sorted(U):
            x=U[ev][1]-common
            if x: print('  %-12s n=%3d rare-only pairs: %s'%(ev,U[ev][0],' '.join(sorted(x))))
