import idle, random, sys, subprocess
from rules import norm
Y='1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1LA0LG_1LB1LG'
def literal(cfgs, maxs=10**10):
    inp=''.join(f"{len(ds)} {' '.join(map(str,ds))} {b}\n" for ds,b in cfgs)
    p=subprocess.run(['./lit2.exe',Y,str(maxs),'1'],input=inp,capture_output=True,text=True,creationflags=0x40)
    out=[]
    for line in p.stdout.strip().split('\n'):
        f=line.split()
        if f[0]=='K': n=int(f[4]); v=list(map(int,f[5:])); out.append(('K',norm(v[:n]),v[n],int(f[1])))
        else: out.append((f[0],int(f[2]),f[3],int(f[1])))
    return out
def predict(ds,b):
    ds=norm(list(ds))
    if not ds:
        if b%2: return ('HALT',b+1)
        if b==0: return ('K',[1],1)
        if b==2: return ('K',[1],5)
        return ('K',[1,3]+[2]*(b//2-2),4)
    if ds[-1]>=1: return ('K',norm(ds[:-1]+[ds[-1]-1]),b+3)
    k=0
    while ds[-1-k]==0: k+=1
    return ('K',norm(ds[:-1-k]+[ds[-1-k]-1,b-2*k+1]+[2]*(k-1)),4)
def same(p,r): return p[0]==r[0] and ((p[0]=='HALT' and p[1]==r[1]) or (p[0]=='K' and p[1]==r[1] and p[2]==r[2]))
if __name__=='__main__':
    # grid
    cfgs=[([3,1]+[0]*k,b) for k in range(1,12) for b in range(1,2*k+4)]
    res=literal(cfgs,10**7)
    for k in range(1,12):
        print(f'k={k:2d}', ''.join('.' if same(predict(ds,b),r) else ('H' if r[0]=='HALT' else 'x') for (ds,b),r in zip(cfgs,res) if len(ds)==k+2))
    random.seed(1); cfgs=[]
    for _ in range(600):
        n=random.randint(1,30)
        ds=[random.choice([0,1,2,2,3,random.randint(0,200),random.randint(0,3000)]) for _ in range(n)]
        if random.random()<0.5: z=random.randint(1,n); ds[n-z:]=[0]*z
        k=0
        while k<len(ds) and ds[-1-k]==0: k+=1
        lo=max(1,2*k) if k else 1
        b=random.choice([lo,lo+1,random.randint(lo,lo+50),random.randint(lo,15000)])
        if all(x==0 for x in ds): b=random.randint(0,600)
        cfgs.append((ds,b))
    res=literal(cfgs)
    print('random 600 (b>=2k): misses', sum(not same(predict(*c),r) for c,r in zip(cfgs,res)))
    ds=[]; b=0; nK=0; tot=0
    for rnd in range(6):
        cf=[]; cur=(ds,b)
        for _ in range(1000):
            cf.append(cur); p=predict(*cur)
            if p[0]!='K': break
            cur=(p[1],p[2])
        res=literal(cf)
        for c,r in zip(cf,res):
            if not same(predict(*c),r): print('LOCKSTEP MISMATCH',c,r); sys.exit()
            if (c[1]+sum(c[0]))%2: print('PHI odd',c); sys.exit()
            nK+=1; tot+=r[3]
        ds,b=cur
        print(f'Y19 lockstep {nK} K-steps exact, {tot} steps, len={len(ds)} b={b} tail {ds[-3:]}',flush=True)
