import idle, random, sys
import rules
from rules import norm, literal
Z='1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE'
def predictZ(ds,b):
    ds=norm(list(ds))
    if not ds:
        if b%2: return ('HALT', b+3)
        return ('K', [1]+[2]*(b//2+1), 1)
    return rules.predict(ds,b)
if __name__=="__main__":
    random.seed(int(sys.argv[1])); N=int(sys.argv[2])
    cfgs=[]
    for _ in range(N):
        n=random.randint(1,30)
        ds=[random.choice([0,1,2,2,3,random.randint(0,200),random.randint(0,3000)]) for _ in range(n)]
        if random.random()<0.5: z=random.randint(1,n); ds[n-z:]=[0]*z
        k=0
        while k<len(ds) and ds[-1-k]==0: k+=1
        lo=max(1,2*k-2) if k else 1
        b=random.choice([lo,lo+1,random.randint(lo,lo+50),random.randint(lo,15000)])
        if all(x==0 for x in ds): b=random.randint(0,600)
        cfgs.append((ds,b))
    # small-b grid for borrows: b in 1..2k+2
    for k in range(1,12):
        for b in range(1,2*k+3): cfgs.append(([3,1]+[0]*k,b))
    res=literal(Z,cfgs,10**9)
    bad=0; badin=0; kinds={}
    for (ds,b),r in zip(cfgs,res):
        p=predictZ(ds,b)
        ok=(p[0]==r[0]) and ((p[0]=='HALT' and p[1]==r[1]) or (p[0]=='K' and p[1]==r[1] and p[2]==r[2]))
        k=0
        while k<len(ds) and ds[-1-k]==0: k+=1
        inpre = (not norm(ds)) or k==0 or b>=2*k-2
        if not ok:
            bad+=1
            if inpre: badin+=1; print('MISS in PRE',ds,b,p,r)
            elif b%2==1 and r[0]!='HALT': print('small odd b not halting',ds,b,r)
            elif b%2==0 and r[0]=='HALT': print('small even b halting',ds,b,r)
    print('N',len(cfgs),'misses',bad,'misses inside PRE',badin)
    