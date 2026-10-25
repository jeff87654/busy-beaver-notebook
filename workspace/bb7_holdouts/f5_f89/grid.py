# grid.py: literal check of the F5 engine rules on constructed abstract configs, all 3 siblings
import sys,random,subprocess,re
from f5eng import parse,step,show,margin
KL=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\f5_f89\kl2.exe'
MS=[('1RB1RG_0LC0LD_1RF0LD_0RE1LB_1LB0RF_0RA---_1RA1RD','D','L'),
    ('1RB1RE_1RC1RA_0LD0LE_1RF0LE_0RG1LC_0RB---_1LC0RF','E','L'),
    ('1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB','G','R')]
def content(st):
    A,L,c=st
    s='10'*A+'0'+''.join('10'*d+'0' for d in L[:-1])+'10'*L[-1]+'1'
    if c>=0: s+='10'*c+'1'
    return s
def tapefor(st,q,side):
    s=content(st)
    return q+'000'+s if side=='L' else s[::-1]+'00'+q+'0'
def litnext(M,q,side,st,steps):
    p=subprocess.run([KL,M,str(steps),q,side,'a',tapefor(st,q,side)],capture_output=True,text=True)
    for l in p.stdout.splitlines():
        if l.startswith('HALT'): return 'HALT'
        if l.startswith('LIMIT'): return 'LIMIT'
        a=l.split(None,1)
        if len(a)==2:
            r=parse(a[1])
            if r is not None: return r
    return 'NONE'
THR=2
def A_even(st): return st[0]%2==0 and (st[2]<0 or st[2]%2==1)
def rand_cfg(rng):
    A=rng.choice([2,4,6,8,10,12,16,20,30,40,60,100])
    if rng.random()<0.2: A=rng.randrange(1,30)
    j=rng.choice([0,0,1,1,2,3,4,5,6,8,10,13,17,25,31])
    kind=rng.choice(['ord','ord','e','e1','e0'])
    L=[0]*j
    if kind=='ord':
        L+= [rng.choice([2,3,4,5,8,13,40])]+[rng.choice([0,2,4,7]) for _ in range(rng.randrange(0,3))]+[rng.choice([0,1,3,5,2])]
    elif kind=='e': L+=[rng.choice([2,3,4,5,9,30])]
    elif kind=='e1': L+=[1]
    else: L+=[0]
    if rng.random()<0.15 and L[0]==0: L[0]=rng.choice([1,2,5])
    c=-1
    if L[-1]==1 or (L[-1]==0 and rng.random()<0.5): c=rng.choice([-1,1,3,5,9,15,33,61])
    if rng.random()<0.1: c=rng.choice([0,2,4])
    return (A,tuple(L),c)
if __name__=='__main__':
    N=int(sys.argv[1]); seed=int(sys.argv[2]); rng=random.Random(seed)
    fails={}; ok=0; tested=0
    for it in range(N):
        st=rand_cfg(rng); pred,r=step(st)
        for M,q,side in MS:
            got=litnext(M,q,side,st,4000000)
            tested+=1
            if got==pred: ok+=1
            else:
                mg=margin(st); key=(r[0],mg[2]>=THR if mg else True,A_even(st)); fails.setdefault(key,[]).append((M[:8],mg,show(st),show(pred) if pred else None,show(got) if isinstance(got,tuple) else got))
    print('tested',tested,'ok',ok)
    for k,v in sorted(fails.items()):
        print('FAIL',k,len(v))
        for x in v[:4]: print('    ',x)
