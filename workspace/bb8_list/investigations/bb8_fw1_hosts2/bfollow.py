"""bfollow.py: round follower for family B 8-state variants (engine D/BOR intact; TOP-ACC checked per round).
Config tokens: list of (run, sep) ; sep in ' ' (0) or '|' (1). Tape bits = tokens + S '1'.
Round = ABSORB -> ... -> ABSORB. Base TOP-ACC sum: c_new = c0 + sum_{j=1..n}(Y(j)+2-2j) with Y(1)=17, Y(2)=6137,
Y(j) = -7 mod 2^3000 for j>=3  ->  c_new = c0 + 6168 - n(n+6) for n>=2.
"""
import idle, sys, re
from fam import BASES, run, parse_u, comp
MOD=1<<60
def tok2bits(runs,seps):
    w='10'*runs[0]
    for s,r in zip(seps,runs[1:]): w+=('0' if s==' ' else '1')+'10'*r
    return w+'1'
def bits2tok(b):
    assert b.endswith('1'); b=b[:-1]
    runs=[];seps=[];cur=0;i=0
    while i<len(b):
        if b.startswith('10',i): cur+=1;i+=2
        elif b[i]=='0': runs.append(cur);seps.append(' ');cur=0;i+=1
        else: runs.append(cur);seps.append('|');cur=0;i+=1
    runs.append(cur); return runs,seps
def fmt(runs,seps):
    o=str(runs[0])
    for s,r in zip(seps,runs[1:]): o+=s+str(r)
    return comp(o)
class Var:
    def __init__(s,m,nm): s.m=m; s.O,s.Q=BASES[nm][1],BASES[nm][2]
    def probe(s,runs,seps,N=10**8):
        r=run(s.m,s.O,s.Q,[tok2bits(runs,seps)],N,1,'B')[0][0].split()
        if r[0]=='M': return ('M',)+bits2tok(r[3])
        return (r[0],r[1] if len(r)>1 else '')
def split_std(runs,seps,big=None):
    """standard post-ABS form: L + [c0 '|'] + 1 + 2^n + [0, y]. returns (Lruns,Lseps,c0 or None,n,y) or None"""
    if len(runs)<3 or runs[-2]!=0 or seps[-1]!=' ' or seps[-2]!=' ': return None
    y=runs[-1]; D=runs[:-2]; DS=seps[:-2]
    i=len(D)-1
    while i>=0 and D[i] in (2,-2) and (i==len(D)-1 or DS[i]==' '): i-=1
    n=len(D)-1-i
    if big is not None: n+=big-1
    if i<0 or D[i]!=1: return None
    if n>0 and DS[i]!=' ': return None
    # left of top
    if i==0: return ([],[],None,n,y)
    if DS[i-1]=='|':
        c0=D[i-1]; return (D[:i-1],DS[:i-2] if i>=2 else [],c0,n,y) if True else None
    return (D[:i],DS[:i-1],None,n,y)
def build(L,LS,c,tail_runs,tail_seps):
    """L (+sep ' ') + [c '|'] + tail"""
    runs=list(L); seps=list(LS)
    if L: seps.append(' ')
    if c is not None:
        runs.append(c); seps.append('|')
    runs+=tail_runs; seps+=tail_seps
    return runs,seps
_TC={}
def topacc_ok(v,L,LS,c):
    key=(v.m,tuple(L),tuple(LS),None if c is None else c%64)
    if key in _TC: return _TC[key]
    r=_topacc_ok(v,L,LS,c); _TC[key]=r; return r
def _topacc_ok(v,L,LS,c):
    # check base TOP-ACC with prefix L and counter c (or None) for K=1..3 and y residues
    for K in (1,2,3):
        for y in ([17] if K==1 else [])+([6137] if K==2 else [])+[121,249]:
            runs,seps=build(L,LS,c,[1]+[0]*K+[0,y],[' ']*(K+2))
            o=v.probe(runs,seps,10**7)
            exp=build(L,LS,(c if c is not None else -1)+y+2-2*K,[1]+[2]*(K-1)+[0,5],[' ']*(K+1))
            if o[0]!='M' or (o[1],o[2])!=exp: return False,(K,y,o[0],fmt(*o[1:]) if o[0]=='M' else o)
    return True,None
def absprobe(v,L,LS,c_res,M=60):
    """probe ABSORB with counter c (given mod 2^M) using representatives c = r + 64k, k=3,5; return output form
       as function of c: tokens with counts affine in c."""
    r=c_res%64
    outs=[]
    for k in (3,5,8):
        c=r+64*k
        runs,seps=build(L,LS,c,[1,0,5],[' ',' '])
        outs.append((c,v.probe(runs,seps,10**8)))
    kinds=set(o[0] for c,o in outs)
    if kinds!={'M'}: return ('NOTM',[ (c,o[0],o[1]) for c,o in outs])
    bl=[blocks(o[1],o[2]) for c,o in outs]
    shapes=set(tuple((v[2]) for v in b) for b in bl)
    if len(shapes)!=1 or len(set(len(b) for b in bl))!=1:
        return ('SHAPEVAR',[(c,fmt(*o[1:])) for c,o in outs])
    from fractions import Fraction
    (c1,c2,c3)=[c for c,o in outs]
    aff=[]
    for b1,b2,b3 in zip(*bl):
        ent=[]
        for idx in (0,1):   # value, count
            a,b,d=b1[idx],b2[idx],b3[idx]
            if (b-a)*(c3-c2)!=(d-b)*(c2-c1): return ('NONAFF',[(c,fmt(*o[1:])) for c,o in outs])
            al=Fraction(b-a,c2-c1); ent.append((al,a-al*c1))
        aff.append((ent[0],ent[1],b1[2]))
    return ('AFF',aff)
def blocks(runs,seps):
    """compress tokens: list of (value, count, sep_after) for maximal groups of equal values joined by ' '"""
    out=[]; i=0; seps=list(seps)+['$']
    while i<len(runs):
        j=i
        while j+1<len(runs) and runs[j+1]==runs[i] and seps[j]==' ': j+=1
        out.append((runs[i],j-i+1,seps[j])); i=j+1
    return out
def unblocks(bl):
    runs=[];seps=[]
    for v,cnt,sp in bl:
        for k in range(cnt):
            runs.append(v); seps.append(' ' if k<cnt-1 else sp)
    return runs,seps[:-1]
def evalaff(aff,c):
    out=[]
    for al,be in aff:
        x=al*c+be
        assert x.denominator==1, (al,be,c)
        out.append(int(x))
    return out
def expand_sym(bl):
    """expand blocks; a huge count is allowed only for a block of value 2 directly after the top 1 (the list);
       it is replaced by a marker count stored separately."""
    runs=[];seps=[];big=None
    for v,cnt,sp in bl:
        if cnt>10**5:
            if v!=2 or big is not None: return None,None,None
            big=cnt; cnt=1; v=-2   # placeholder single token
        if v>10**6 and not (cnt==1): return None,None,None
        for k in range(cnt):
            runs.append(v); seps.append(' ' if k<cnt-1 else sp)
    return runs,seps[:-1],big
def split_gen(runs,seps):
    # [L][c0 '|'] 1 D 0 y  with D nonempty even digits joined by ' '
    if len(runs)<4 or runs[-2]!=0 or seps[-1]!=' ' or seps[-2]!=' ': return None
    y=runs[-1]; R=runs[:-2]; RS=seps[:-2]
    i=len(R)-1
    while i>=0 and R[i]%2==0 and (i==len(R)-1 or RS[i]==' '): i-=1
    D=R[i+1:]
    if i<0 or R[i]!=1 or not D or RS[i]!=' ': return None
    if i==0: return ([],[],None,D,y)
    if RS[i-1]=='|': return (R[:i-1],RS[:i-2] if i>=2 else [],R[i-1],D,y)
    return (R[:i],RS[:i-1],None,D,y)
def follow(m,nm,rounds=12,start=None,verbose=True):
    v=Var(m,nm)
    # start: literal from blank to first ABS moment (tokens end 'c|1 0 5' or '1 0 5' with list empty)
    if start is None:
        r=run(m,v.O,v.Q,['B'],2*10**8,400,'B')[0]
        st=None
        for x in r:
            p=x.split()
            if p[0]=='T': break
            if p[0]!='M': return ('BLANK-'+p[0],x[:80])
            runs,seps=bits2tok(p[3])
            if len(runs)>=3 and runs[-3:]==[1,0,5] and len(runs)>=4 and seps[-3]=='|':
                st=(runs[:-4],seps[:-4],runs[-4]); break
        if st is None:
            # symbolic start: last moment of standard form [L][c0|] 1 D (0,y) with D even digits, len(D)>=3
            cand=None
            for x in r:
                p=x.split()
                if p[0]!='M': break
                runs,seps=bits2tok(p[3])
                f=split_gen(runs,seps)
                if f is not None and len(f[3])>=3: cand=f; break
            if cand is None: return ('NO-ABS-FROM-BLANK',)
            L,LS,c0,D,y=cand
            ok,why=topacc_ok(v,L,LS,c0)
            if not ok: return ('TOPACC-MOD-start',why)
            K=len(D); cc=-1 if c0 is None else c0
            c=(cc+(-7+2-2*K)+(6168-(K-1)*(K+5) if K-1>=2 else (17 if K-1==1 else 0)))%MOD
            exact=False; cval=c
        else:
            L,LS,c=st; exact=True; cval=c
    else:
        L,LS,c=start; exact=True; cval=c
    hist=[]
    for rd in range(1,rounds+1):
        # ABSORB at round rd with prefix L, counter c (exact if 'exact' else residue mod MOD)
        if exact and cval<4000:
            runs,seps=build(L,LS,cval,[1,0,5],[' ',' '])
            o=v.probe(runs,seps,10**9)
            if o[0]!='M': return ('ABS-%s'%o[0],rd,hist)
            outr,outs=o[1],o[2]; big=None
        else:
            a=absprobe(v,L,LS,cval)
            if a[0]!='AFF': return ('ABS-'+a[0],rd,hist,a[1])
            # residue representative only: evaluate counts mod MOD with c residue
            bl=[]
            for (va,vb),(ca,cb),sp in a[1]:
                x=va*cval+vb; y_=ca*cval+cb
                if x.denominator!=1 or y_.denominator!=1: return ('ABS-FRAC',rd,hist)
                bl.append((int(x),int(y_),sp))
            # counts must be small to expand; huge counts only allowed for the 2-run (list) -> handle symbolically
            outr,outs,big=expand_sym(bl)
            if outr is None: return ('ABS-HUGEBLOCK',rd,hist,str(a[1])[:200])
        sp=split_std(outr,outs,big)
        hist.append((rd, 'exact' if exact and cval<4000 else 'res', cval if exact else cval%1024, (fmt(outr,outs) if len(outr)<12 else fmt(outr[:10],outs[:9])+'..')+('' if big is None else ' [n=%d mod..]'%(big%1024))))
        if sp is None:
            return ('NONSTD-after-ABS',rd,hist,fmt(outr,outs) if max(outr)<10**6 and len(outr)<60 else str(outs[:20]))
        L2,LS2,c0,n,y=sp
        if y!=5: return ('Y!=5',rd,hist)
        ok,why=topacc_ok(v,L2,LS2,c0 if c0 is None or c0<10**6 else c0%64+640)
        if not ok: return ('TOPACC-MOD',rd,hist,why)
        cc=-1 if c0 is None else c0
        if n==0: newc=None
        elif n==1: newc=cc+17
        else: newc=cc+6168-n*(n+6)
        if n>=3: exact=False
        cval=newc% MOD if not exact else newc
        L,LS=L2,LS2
    return ('ROUNDS-OK',rounds,hist)
if __name__=='__main__':
    nm=sys.argv[1]
    for m in sys.argv[2:]:
        r=follow(m,nm)
        print(m,r[0],r[1:] if len(r)>1 else '')
