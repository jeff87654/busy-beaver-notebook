import idle, random
from rsim import RSim
from sim import M1, M2
# tape spec: string with exactly one head marker like 'E>' (head reads next char) or '<F' (head reads previous char)
def build(M, spec):
    import re
    m=re.search(r'([A-G])>|<([A-G])',spec)
    st=m.group(1) or m.group(2)
    a=spec[:m.start()]; b=spec[m.end():]
    if m.group(1): left, head, right = a, b[0], b[1:]
    else: left, head, right = a[:-1], a[-1], b
    L=[]; [RSim.push(L,int(c),1) for c in left]
    R=[]; [RSim.push(R,int(c),1) for c in reversed(right)]
    return RSim(M,L,int(head),R,'ABCDEFG'.index(st))
def canon(r):
    left=''.join(str(b)*c for b,c in r.L).lstrip('0'); right=''.join(str(b)*c for b,c in reversed(r.R)).rstrip('0')
    return left,'ABCDEFG'[r.s],r.h,right
def runN(r,n):
    while r.steps<n:
        if not r.step(): return False
    return r.steps==n
rb=lambda: ''.join(random.choice('01') for _ in range(random.randint(0,6)))
def check(name, before, after, steps, pmin=0, trials=60, lpref=True):
    for M,w in ((M1,1),(M2,2)):
        bad=0
        for t in range(trials):
            p=random.randint(pmin,pmin+40); X=rb(); l=('1' if lpref else '')+rb() if lpref else ''
            r=build(M,before(p,l,X)); ok=runN(r,steps(p,w)); e=build(M,after(p,l,X))
            if not ok or canon(r)!=canon(e): bad+=1
        print(f'{name:40s} M{w} bad={bad}/{trials}')
o=lambda n:'1'*n; z=lambda n:'0'*n
random.seed(1)
check('L1 0^inf E>0 1^m 001X -> E>0 1^(m+3) 00X', lambda m,l,X:'E>0'+o(m)+'001'+X, lambda m,l,X:'E>0'+o(m+3)+'00'+X, lambda m,w:2*m+10, lpref=False)
check('L2 0^inf E>0 1^m 000X -> F>0 1^(m+3) 00X', lambda m,l,X:'E>0'+o(m)+'000'+X, lambda m,l,X:'F>0'+o(m+3)+'00'+X, lambda m,w:2*m+10, lpref=False)
check('L3 l F>0 1^M 000X -> l10 F>0 1^(M-1) 00X', lambda m,l,X:l+'F>0'+o(m)+'000'+X, lambda m,l,X:l+'10F>0'+o(m-1)+'00'+X, lambda m,w:2*m+4, pmin=2)
check('L4 l F>0 1^M 001X -> l1 F>00 1^(M-1) 00X', lambda m,l,X:l+'F>0'+o(m)+'001'+X, lambda m,l,X:l+'1F>00'+o(m-1)+'00'+X, lambda m,w:2*m+5, pmin=2)
check('L5 l01 F>00 1^N 001X -> l<F 0 1^(N+4) 00X', lambda m,l,X:l+'01F>00'+o(m)+'001'+X, lambda m,l,X:l+'<F0'+o(m+4)+'00'+X, lambda m,w:2*m+11)
check("L5' l01 F>00 1^N 000X -> l F>0 1^(N+4) 00X", lambda m,l,X:l+'01F>00'+o(m)+'000'+X, lambda m,l,X:l+'F>0'+o(m+4)+'00'+X, lambda m,w:2*m+10)
check('L6 0^inf 1<F 0Y -> E>0 100Y', lambda m,l,X:'1<F0'+o(m)+X, lambda m,l,X:'E>0100'+o(m)+X, lambda m,w:6 if w==1 else 8, lpref=False)
check('L7 l0101<F 0Y -> l<F 0 1100Y', lambda m,l,X:l+'0101<F0'+o(m)+X, lambda m,l,X:l+'<F01100'+o(m)+X, lambda m,w:8 if w==1 else 10)
check('L8 l1 F>0 1 000.. -> l<F 0 1 0..(end)', lambda m,l,X:l+'10F>01000', lambda m,l,X:l+'1<F010', lambda m,w:6 if w==1 else 8)
check('H  l0 11<F 0 1Y -> halt after 6 (C1)', lambda m,l,X:l+'011<F01'+X, lambda m,l,X:l+'100C>1'+X, lambda m,w:6)
bad=0
for M in (M1,M2):
    for t in range(100):
        l='1'+rb(); Y=rb()
        r=build(M,l+'011<F01'+Y)
        while r.step(): pass
        if not (r.steps==6 and r.s==2 and r.h==1 and canon(r)==canon(build(M,l+'1001C>1'+Y))): bad+=1
print('H  l011<F 01Y -> l1001 C>1Y, 6 steps then C1 undefined: bad',bad,'/200')
