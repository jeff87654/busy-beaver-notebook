# validate C(d;xs;a) round rules R1-R4 for the F4.13-type list machine. usage: v53.py MACHINE [N]
import sys, random, subprocess
from c53 import word, parse, V
def norm(c):
    d,xs,a=c; xs=list(xs)
    if d==0:
        while xs and xs[0]==0: xs.pop(0)
    return (d,tuple(xs),a)
def pred(c):
    d,xs,a=c; xs=list(xs)
    if xs and xs[-1]>=1: return 'R1',norm((d,tuple(xs[:-1]+[xs[-1]-1]),4*a+4))
    nz=[i for i,x in enumerate(xs) if x>0]
    if nz:
        j=nz[-1]; m=len(xs)-1-j
        return 'R2',norm((d,tuple(xs[:j]+[xs[j]-1,4*a+4-m]+[1]*(m-1)),1))
    if d>=1:
        m=len(xs); return 'R3',norm((d-1,tuple([4*a+3-m]+[1]*m),1))
    return 'R4',(4*a+2,(),8)
def nextc(m,cfgs,skip=0):
    inp=''.join(f"H {word(*c).lstrip('0') or '-'} - ALL\n" for c in cfgs)
    # run each separately to get event lists
    res=[]
    for c in cfgs:
        o=subprocess.run([V,m,'H','R','200000000'],input=f"H {word(*c).lstrip('0')} - ALL\n",capture_output=True,text=True).stdout.split('\n')
        got=None
        for l in o:
            p=l.split()
            if not p: continue
            if p[0]=='H': got=('HALT',p[1]); break
            if p[0]=='E' and p[2].endswith('100'):
                q=parse(p[2]) or parse('0'+p[2])
                if q:
                    if skip and q==(0,(1,)*(len(p[2])//2-1),1) or (skip and q[0]==0): continue
                    got=norm(q); break
        res.append(got)
    return res
if __name__=='__main__':
    m=sys.argv[1]; N=int(sys.argv[2]) if len(sys.argv)>2 else 120
    random.seed(1); cases={'R1':[], 'R2':[], 'R3':[], 'R4':[]}
    while min(len(v) for v in cases.values())<N:
        d=random.randint(0,4); k=random.randint(0,6); xs=[random.choice([0,0,1,2,3,5]) for _ in range(k)]; a=random.randint(1,40)
        if d==0 and xs and xs[0]==1: continue
        c=norm((d,tuple(xs),a)); r,p=pred(c)
        if r=='R3' and 4*a+3-len(c[1])<2: continue
        if len(cases[r])<N: cases[r].append((c,p))
    for r,v in cases.items():
        got=nextc(m,[c for c,p in v],skip=(r=='R4')); bad=[(c,p,g) for (c,p),g in zip(v,got) if g!=p]
        print(r,len(v),'bad',len(bad),bad[:2])
