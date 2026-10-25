import sys,re,random
Q=sys.argv[1]
from val import probe
random.seed(2)
def cfg(z,x,k,j): return Q+' |'+'0'*z+'1'*x+'0'+'1'*k+('0'+'1'*j if j else '')
def parse(r):
    if r[0]!='S': return r[0]
    if r[2].strip('0'): return ('Ljunk',)
    t=r[4].rstrip('0'); g=re.fullmatch(r'(0+)(1+)(?:0(1*)(?:0(1+))?)?',t)
    if not g: return ('?',t[:50])
    return (len(g.group(1)),len(g.group(2)),len(g.group(3) or ''),len(g.group(4) or ''))
def rule(z,x,k,j):
    r=rule0(z,x,k,j)
    return (3,r[1]-1,r[2],r[3]) if Q=='H' and r[0]==1 else r
def rule0(z,x,k,j):
    if x>=2: return (z+2,x-1,k,j)
    if k>=1: return (1,z+3,k-1,j)
    if j>=1: return (1,2,z+3,j-1)
    return (1,2,z+1,2)
cases=[]
for i in range(200): cases.append((2*random.randint(0,80)+1,random.randint(2,90),random.randint(0,60),random.randint(0,2)))
for i in range(200): cases.append((2*random.randint(0,80)+1,1,random.randint(1,60),random.randint(0,2)))
for i in range(150): cases.append((2*random.randint(0,80)+1,1,0,random.randint(1,2)))
for i in range(100): cases.append((2*random.randint(0,80)+1,1,0,0))
for m in sys.argv[2:]:
    res=probe(m,Q,'L',[cfg(*c) for c in cases],10**8)
    bad=0
    for c,r in zip(cases,res):
        if parse(r)!=rule(*c):
            bad+=1
            if bad<6: print('BAD',c,parse(r),rule(*c))
    print(m,len(cases),'cases',bad,'bad')
