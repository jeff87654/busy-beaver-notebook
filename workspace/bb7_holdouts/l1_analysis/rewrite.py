"""Boundary rewrite experiment; all arithmetic is exact.

C(a,S) = 0^inf G>0 000 (100)^a S 0^inf.
Rules below are validated independently in validate.py; derivation in REPORT.txt.
"""
from collections import deque
from functools import lru_cache
from probe import TABLE

def primitive(w):
    for p in range(1,len(w)+1):
        if len(w)%p==0 and w==w[:p]*(len(w)//p): return w[:p],len(w)//p

class Rope:
    def __init__(self,parts=()):
        self.d=deque()
        for w,n in parts:self.append(w,n)
    def append(self,w,n=1):
        if not w or not n:return
        w,c=primitive(w); n*=c
        if self.d and self.d[-1][0]==w:self.d[-1][1]+=n
        else:self.d.append([w,n])
    def prepend(self,w,n=1):
        if not w or not n:return
        w,c=primitive(w);n*=c
        if self.d and self.d[0][0]==w:self.d[0][1]+=n
        else:self.d.appendleft([w,n])
    def unit(self):
        if not self.d:return '0'
        w,n=self.d[0];self.d[0][1]-=1
        if n==1:self.d.popleft()
        return w
    def popbit(self):
        if not self.d:return '0'
        w=self.unit();self.prepend(w[1:]);return w[0]
    def peek(self,n):
        s=''
        for w,c in self.d:
            s+=(w*min(c,(n-len(s)+len(w)-1)//len(w)))[:n-len(s)]
            if len(s)==n:break
        return s+'0'*(n-len(s))
    def drop(self,n):
        for _ in range(n):self.popbit()
    def run(self,pat):
        """Consume maximal copies of a short pattern without expanding counts."""
        ans=0
        while self.peek(len(pat))==pat:
            w,n=self.d[0]
            # When a whole leading segment is compatible with pat, consume
            # all complete pat copies in that segment, leaving a short suffix.
            L=len(w)*n; p=len(pat)
            check=min(L,len(w)*p)
            if L>=p and all(w[i%len(w)]==pat[i%p] for i in range(check)):
                take=L//p; rem=L%p; self.d.popleft();ans+=take
                if rem:self.prepend(''.join(w[(L-rem+i)%len(w)] for i in range(rem)))
            else:self.drop(p);ans+=1
        return ans
    def string(self,limit=1000000):
        if sum(len(w)*n for w,n in self.d)>limit:raise OverflowError('rope too large')
        return ''.join(w*n for w,n in self.d)
    def __repr__(self):return ' '.join(f'({w})^{n}' for w,n in self.d)

@lru_cache(None)
def crossing(q,side,word):
    a=list(word);p=len(a)-1 if side else 0;t=0;seen=set()
    while 0<=p<len(a):
        key=(q,p,''.join(a))
        if key in seen:raise RuntimeError('local cycle')
        seen.add(key);tr=TABLE[q][int(a[p])]
        if tr is None:return q,p,''.join(a),t,'H'
        w,d,q=tr;a[p]=str(w);p+=d;t+=1
    return q,p,''.join(a),t,'R' if p>=len(a) else 'L'

def local(tail,budget=100000):
    """Run from B at left end of tail until exiting that end or halting.

    L/R stacks contain oriented words. Their nearest unit is at deque front.
    We do not discard blank segments: the left boundary is a fixed boundary.
    """
    L=Rope();R=tail;cur=R.unit();q=1;side=0;t=0
    for it in range(budget):
        nq,p,w,dt,result=crossing(q,side,cur)
        if result=='H':return 'H',t+dt,None
        right=result=='R';nside=0 if right else 1
        ahead=R if right else L;behind=L if right else R
        n=1
        if nq==q and nside==side and ahead.d and ahead.d[0][0]==cur:
            n+=ahead.d.popleft()[1]
        behind.prepend(w,n);t+=dt*n
        if not right and not L.d:return chr(65+nq),t,R
        cur=ahead.unit();q=nq;side=nside
    raise RuntimeError('local budget')

def advance(a,tail):
    """Return (new a, new tail, defined TM steps, rule); None a = halt."""
    a+=tail.run('100')
    p=tail.peek(3)
    if p=='010':
        n=tail.run('010')
        return a+3*n,tail,12*a*n+18*n*n+30*n,'transfer'
    if p=='110':
        n=tail.run('110')
        return a+2*n,tail,6*a*n+6*n*n+15*n,'110'
    if p=='000':
        if not any('1' in w for w,n in tail.d):
            return 2,Rope([('0',1),('1100',a-1),('101001',1)]),3*a*a+31*a+80,'blank'
        if tail.peek(4)!='0001':raise NotImplementedError(('000-other',a,repr(tail)))
        tail.drop(3);tail.prepend('001',a);tail.prepend('010')
        return 2,tail,18*a+74,'reset000'
    if p=='001':
        tail.drop(3);tail.prepend('011');tail.prepend('010',a-1);tail.prepend('110')
        return 2,tail,12*a+64,'reset001'
    if p in ('011','111'):
        tail.drop(3);tail.prepend('111' if p=='011' else '101')
        return a+1,tail,6*a+21,p
    assert p=='101',p
    q,dt,newtail=local(tail)
    if q=='H':return None,None,3*a+12+dt,'HALT'
    assert q=='C',(q,a,newtail)
    return a+1,newtail,6*a+18+dt,'local101'

class SymbolicStop(Exception):
    def __init__(self,u,v,w,m,suffix):
        self.data={'u':u,'v':v,'w':w,'m':m,'suffix':list(suffix.d)}
        super().__init__('Next exact cycle batch requires a symbolic power')

def advance_fast(a,tail,max_power_bits=1000000):
    # C(4, (010)^u 011 (100)^v 110 (010)^w S)
    # -> C(4, (010)^(9u+52) 011 (100)^(v-3) 110 (010)^(w-1) S).
    # 20 basic rewrites; requires u>=1, v>=3, w>=1.
    if a==4:
        r=Rope(tail.d);u=r.run('010')
        if u and r.peek(3)=='011':
            r.drop(3);v=r.run('100')
            if v>=3 and r.peek(3)=='110':
                r.drop(3);w=r.run('010')
                if w:
                    m=min(v//3,w)
                    if 4*m>max_power_bits:raise SymbolicStop(u,v,w,m,r)
                    p=9**m;c=2*u+13
                    nu=(c*p-13)//2
                    dt=45*c*c*((p*p-1)//80)+6*c*(p-1)+(12*v-157)*m-18*m*(m-1)
                    out=Rope([('010',nu),('011',1),('100',v-3*m),('110',1),('010',w-m)])
                    for word,n in r.d:out.append(word,n)
                    return 4,out,dt,f'cycle20^{m}'
    return advance(a,tail)

if __name__=='__main__':
    a=4;tail=Rope([('110100100',1)]);t=189
    for i in range(200):
        if i<80:print(i,t,a,tail)
        a,tail,dt,r=advance(a,tail);t+=dt
        if a is None:print('HALT',t);break
