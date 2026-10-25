import idle, random, sys, os
from fam import *
from usage import testsA, testsB, testsC
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\counters')
def rareB():
    T=[]
    for c in [None,0,1,2,3,6,7]:
        for K in [1,2,3,4]:
            for y in [2*K+9, 2*K+23, 57, 121]+([17] if K==1 else []):
                T.append(('TOP c=%s K=%d y=%d'%(c,K,y),encB(c,[1]+[0]*K,y)))
    for c in [0,1,2,3,4,5,8,9,12,16,20,30,31,40,41,62]:
        T.append(('ABS c=%d'%c,encB(c,[1],5)))
    # no-top exhaustions (E*): [c|][0^K] and [c|][0^j,2x..]-consumed
    for c in [None,0,3,16]:
        for K in [1,2,3]:
            for y in [57,121]:
                T.append(('NOTOP c=%s K=%d y=%d'%(c,K,y),encB(c,[0]*K,y)))
    return T
def rareA():
    import absA
    T=[]
    for K in [1,2,3]:
        for y in [2*K+10, 2*K+24]:
            for pre in [[],[2],[4,0]]:
                D=pre+[1]+[0]*K; runs,seps=absA.canon(D+[0,y],[' ']*(len(D)+1))
                T.append(('TOPACC pre=%s K=%d y=%d'%(pre,K,y),encA(runs,seps)))
            # alt-sep TOPACC: counter c | 1 0^K
            for c in [3,6]:
                D=[c,1]+[0]*K; seps=['|']+[' ']*(len(D)) ; runs,seps=absA.canon(D+[0,y],seps)
                T.append(('TOPACCalt c=%d K=%d y=%d'%(c,K,y),encA(runs,seps)))
    for y in [10,14,30]:
        T.append(('EMPTY y=%d'%y,encA([0,0,y],[' ',' '])))
    # counter collapse: c | 0^K
    for c in [3,6]:
        for K in [1,2]:
            for y in [14,30]:
                D=[c]+[0]*K; seps=['|']+[' ']*K; runs,seps=absA.canon(D+[0,y],seps)
                T.append(('COLL c=%d K=%d y=%d'%(c,K,y),encA(runs,seps)))
    return T
def rareC():
    T=[]
    for top in [1,3,5]:
        for B in [[0],[0,0],[1,0],[0,1,0],[0,0,0],[1,0,0]]:
            for y in [2*len(B)+11, 2*len(B)+31, 59, 123]:
                T.append(('TOP t=%d B=%s y=%d'%(top,B,y),encC([top]+B,y)))
    for B in [[0],[0,0],[1,0],[0,1,0],[0,0,0],[1,0,0],[0,0,1,0]]:
        for y in [59,123]:
            T.append(('NOTOP B=%s y=%d'%(B,y),encC(B,y)))
    return T
def build(nm):
    m,O,Q,f=BASES[nm]
    rng=random.Random(11)
    gen={'A':testsA,'B':testsB,'C':testsC}[f]
    E=[t for t in gen(rng)+gen(random.Random(12)) if t[0] in ('D','BOR','BORodd')]
    # dedupe, keep variety
    seen=set(); E2=[]
    for t in E:
        if t[1] in seen: continue
        seen.add(t[1]); E2.append(t)
    E=E2[:80]
    # order: short first
    E.sort(key=lambda t:len(t[1]))
    os.environ.pop('EVPAIRS',None)
    E=[(a,fixtape(nm,b)) for a,b in E]
    res=run(m,O,Q,[t[1] for t in E],10**7,1,filt(nm))
    with open('bat/%s.eng'%nm,'w') as fo:
        for (ev,tp),r in zip(E,res):
            o=r[0].split()
            assert o[0]=='M',(nm,ev,r)
            fo.write('%s %s %d\n'%(tp,o[3],3*int(o[1])+2000))
    R={'A':rareA,'B':rareB,'C':rareC}[f]()
    R=[(a,fixtape(nm,b)) for a,b in R]
    res=run(m,O,Q,[t[1] for t in R],10**7,1,filt(nm))
    with open('bat/%s.rare'%nm,'w') as fo, open('bat/%s.rarelab'%nm,'w') as fl:
        for (lab,tp),r in zip(R,res):
            o=r[0].split()
            st=int(o[1]) if o[0] in 'MH' else 10**6
            fo.write('%s %d\n'%(tp,4*st+20000)); fl.write('%s\t%s\n'%(lab,(o[0]+' '+dec2(nm,o[3])) if o[0]=='M' else r[0][:80]))
    print(nm,len(E),len(R))
if __name__=='__main__':
    os.makedirs('bat',exist_ok=True)
    for nm in (sys.argv[1:] or BASES): build(nm)
