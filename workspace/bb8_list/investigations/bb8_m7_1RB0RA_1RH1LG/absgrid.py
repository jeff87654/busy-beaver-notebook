import subprocess,sys,random
from pw import word
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF'
GK='./gk3_s.exe'
def lit(toks,r,P=False,N=20000000):
    w=word(toks,r,P)
    args=[GK,M,w,'B',str(N),'1']+(['P'] if P else [])
    out=subprocess.run(args,capture_output=True,text=True).stdout.strip().split('\n')
    for l in out:
        if l.startswith('step'):
            st=int(l.split()[1]); body=l[l.index('[')+1:l.index(']')]
            toks2=[int(x) for x in body.split(',')] if body else []
            r2=int(l.split('r=')[1].split()[0])
            return st,toks2,r2
        if l.startswith('HALT'): return 'HALT',l
    return None
def pred(toks,r):
    a=toks[-1]
    if a>=4: return toks[:-1]+[a-3],2*r+4
    if a==1:
        j=len(toks)-2
        while j>=0 and toks[j]==1: j-=1
        if j<0: return 'USED'
        t=toks[j]; new=list(toks)
        if t==2:
            del new[j]; new[j]=2*r+3
        else:
            new[j]=t-3; new[j+1]=2*r+3
        return new,2
    return 'A2'
if __name__=='__main__':
    random.seed(int(sys.argv[1])); n=int(sys.argv[2])
    P=len(sys.argv)>3
    bad=0
    for it in range(n):
        L=random.randint(1,5)
        toks=[random.choice([1,1,1,2,4,5,7,8,10]) for _ in range(L)]
        a=random.choice([1,1,4,5,7,2])
        toks=toks+[a]
        r=random.choice([2,5,8,11,14])
        p=pred(toks,r)
        if p in('USED','A2'):
            print('skip',p,toks,r); continue
        res=lit(toks,r,P)
        if res is None or res[0]=='HALT':
            print('NOK',toks,r,res,'pred',p); bad+=1; continue
        st,t2,r2=res
        if (t2,r2)!=p: print('MISMATCH',toks,r,'lit',t2,r2,'pred',p,'step',st); bad+=1
    print('done bad=',bad)
