import idle, random, sys, collections
from fam import BASES, run
from bfollow import tok2bits, fmt
def rand_cfg(rng):
    L=rng.randint(1,7); runs=[]; seps=[]
    for j in range(L):
        runs.append(rng.choice([0,0,1,2,2,3,4,5,6,7,8,11,14,30,61,62]))
        seps.append(rng.choice([' ',' ',' ','|']))
    runs+= [0, rng.choice([5,11,17,57,121,249,6137])]; seps+=[' ',' ']
    return runs,seps[:len(runs)-1]
def halts(m,nm,n=3000,seed=1):
    rng=random.Random(seed); O,Q=BASES[nm][1],BASES[nm][2]
    cfgs=[rand_cfg(rng) for _ in range(n)]
    res=run(m,O,Q,[tok2bits(r,s) for r,s in cfgs],2*10**6,1,'B')
    H=[(fmt(*c),r[0][:40]) for c,r in zip(cfgs,res) if r[0].startswith('H')]
    return H
if __name__=='__main__':
    nm=sys.argv[1]
    for m in sys.argv[2:]:
        H=halts(m,nm); print(m,'halting configs:',len(H)); 
        for h in H[:8]: print('    ',h)
