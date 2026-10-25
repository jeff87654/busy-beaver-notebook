import sys,re,random
from val import probe
random.seed(1)
def cfg(c,x,y): return 'D 00'+'1'*c+'0'+'1'*x+'0'+'1'*y+'0|0'
def parse(r):
    if r[0]!='S': return r[0]
    L=r[2].lstrip('0')
    if r[4].strip('0') or not L.endswith('10'): return ('?',L[:60])
    bl=[len(x) for x in L[:-1].split('0')]
    return tuple(bl) if len(bl)==3 else ((0,)+tuple(bl) if len(bl)==2 else ('?',L[:60]))
def rule(c,x,y):
    if c%2==1 and y==3: return (c-1,x,8)
    if c==0 and y==3: return (x-1,2,2)
    if x>=1 and y>=2: return (c,x-1,y+2)
    if x==0 and c>=2 and c%2==0: return (c-1,y+1,3)
    if c==0 and x==0: return (0,y-1,3)
cases=[]
for i in range(150): cases.append((2*random.randint(1,40),random.randint(1,60),2*random.randint(1,60)))
for i in range(120): cases.append((2*random.randint(1,40),0,2*random.randint(2,60)))
for i in range(120): cases.append((2*random.randint(1,40)-1,2*random.randint(2,45)+1,3))
for i in range(120): cases.append((0,0,2*random.randint(3,80)))
for i in range(120): cases.append((0,2*random.randint(3,80)+1,3))
for m in sys.argv[1:]:
    cur=[cfg(*c) for c in cases]; out=[None]*len(cases); nev=[0]*len(cases); act=list(range(len(cases)))
    for it in range(8):
        if not act: break
        res=probe(m,'D','R',[cur[i] for i in act],10**8); nact=[]
        for i,r in zip(act,res):
            p=parse(r); nev[i]+=1
            if isinstance(p,tuple) and p[0]!='?' or isinstance(p,str): out[i]=p
            else: cur[i]='D '+r[2]+'|'+r[4]; nact.append(i)
        act=nact
    bad=0
    from collections import Counter
    for c,o in zip(cases,out):
        if o!=rule(*c):
            bad+=1
            if bad<5: print('BAD',c,o,rule(*c))
    print(m,len(cases),'cases',bad,'bad; events-per-rule histogram',Counter(nev))
