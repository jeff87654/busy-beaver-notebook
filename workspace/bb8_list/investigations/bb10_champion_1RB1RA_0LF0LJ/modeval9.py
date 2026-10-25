"""Evaluate the clearing function of the abstract model modulo 2^k for huge values.
Numbers: python int (exact, small) or Huge(r,k): huge number known mod 2^k.
f(x)=3x+7 ; G_0=f ; G_j(x)=G_{j-1}^{x+2-2j}(X_{j-1}), X_0=7, X_{i+1}=G_i(G_i(X_i)); digit v at depth j: G_j^v.
"""
import sys
from functools import lru_cache
SMALL=60       # exact if iteration count <= SMALL
T0=int(sys.argv[1]) if len(sys.argv)>1 else 48
LIMIT=1<<64    # exact ints above this become Huge
class Huge:
    def __init__(s,r,k): s.k=k; s.r=r%(1<<k)
    def __repr__(s): return 'H(%d mod 2^%d)'%(s.r,s.k)
def mk(x):
    return x
def par(x): return (x.r if isinstance(x,Huge) else x)&1
def low(x,m):  # x mod 2^m (m<=k)
    if isinstance(x,Huge):
        assert m<=x.k,(x,m)
        return x.r%(1<<m)
    return x%(1<<m)
def prec(x): return x.k if isinstance(x,Huge) else 10**9
def add(x,c):
    if isinstance(x,Huge): return Huge(x.r+c,x.k)
    return x+c
def f_pow(t,x):
    """f^t(x)=(3^t(2x+7)-7)/2"""
    if isinstance(t,Huge):
        # need x precision
        k=min(prec(x),t.k+1) if True else 0
        kk=min(k,200)
        # 3^t mod 2^(kk+1): period 2^(kk-1) for kk+1>=3
        e=low(t,kk-1) if kk>=2 else 0
        xr=low(x,kk)
        v=((pow(3,e,1<<(kk+1))*(2*xr+7)-7)%(1<<(kk+1)))>>1
        return Huge(v,kk)
    # exact t
    if not isinstance(x,Huge) and t<=2000:
        v=(pow(3,t)*(2*x+7)-7)//2
        if v<LIMIT: return v
        return Huge(v,min(256,v.bit_length()))   # huge but known
    kk=min(prec(x),256)
    xr=low(x,kk)
    v=((pow(3,t,1<<(kk+1))*(2*xr+7)-7)%(1<<(kk+1)))>>1
    return Huge(v,kk)
@lru_cache(None)
def Xj(i):
    if i==0: return 7
    y=Xj(i-1)
    y=G(i-1,y); y=G(i-1,y)
    return y
def hkey(x): return ('H',x.r,x.k) if isinstance(x,Huge) else x
_cache={}
def G(j,x):
    key=(j,hkey(x))
    if key in _cache: return _cache[key]
    r=_G(j,x); _cache[key]=r; return r
def _G(j,x):
    if j==0: return f_pow(1,x)
    n=add(x,2-2*j)
    if not isinstance(n,Huge) and n<=0: raise Exception('site condition fails j=%d x=%r'%(j,x))
    if j==1:
        return f_pow(n,7)
    return Iter(j-1,n,Xj(j-1))
def Iter(i,n,s):
    if i==0: return f_pow(n,s)
    if not isinstance(n,Huge) and n<=SMALL:
        y=s
        for _ in range(n): y=G(i,y)
        return y
    # huge/large n: stabilized: need n>=T0
    T=T0+((par(n)-T0)%2)
    y=s
    for _ in range(T): y=G(i,y)
    return y
def CD(j,v,x):
    """digit v at depth j"""
    return Iter(j,v,x)
def clear(digits_topfirst,B):
    b=B
    for depth,d in enumerate(digits_topfirst):
        if d==0: continue
        b=CD(depth,d,b)
    return b
if __name__=='__main__':
    L=[0,1,0,1,0,1,0,2]
    b1=clear(L,3)
    print('b1 =',b1)
    for p in (1,2,3,4,5,6,8,10):
        if prec(b1)>=p: print(p,low(b1,p))
