import os
os.environ['BB8TM']="1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
import planner_b as P
from planner_b import C, BLANK as BL

def bits(s): return tuple(int(c) for c in s)
def toks(items, left=False, term=BL):
    """items: LEFT-TO-RIGHT list of (blockstring, count) (count int or affine). Returns stream tokens.
    For a left side, stream order is nearest-head first = reversed order with reversed blocks."""
    out=[]
    seq = list(reversed(items)) if left else list(items)
    for b,c in seq:
        blk = tuple(reversed(bits(b))) if left else bits(b)
        if isinstance(c,int): out.extend(list(blk)*c)
        else: out.extend(P.mkrun(blk,c))
    if term is not None: out.append(term)
    return P.norm_side(out)

def m_loop(cfg):
    """TLE / TLD."""
    q,L,R,mode=cfg
    if mode!='>' or q not in 'ED': return None
    lb,rb=((0,1),(1,0)) if q=='E' else ((1,0),(0,1))
    pre=[]
    cfg1,texts=P.absorb_all(cfg)
    q,L,R,mode=cfg1
    if not P.is_run(R[0]) or R[0][1]!=rb: return None
    if len(L)==2 and P.is_run(L[0]) and L[0][1]==lb and L[1]==BL:
        a=L[0][2]
    else:
        # concrete cells (lb)*k then BL
        if L[-1]!=BL: return None
        cells=L[:-1]
        if not all(isinstance(c,int) for c in cells): return None
        k,r=divmod(len(cells),2)
        if r or tuple(cells)!=lb*k or k<2: return None
        a=C(k)
    c=R[0][2]
    if c[0]<1: return None
    b=P.cadd(c,P.cconst(-1))
    if a[0]<2 and a[1]==(): return None
    a2=P.cadd(a,P.cscale(b,3))
    rest=R[1:]
    newL=P.norm_side(P.mkrun(lb,a2)+[BL])
    newR=P.norm_side(list(rb)+list(rest))
    txt=list(texts)+['follow (TL%ss %s %s %s %s (%s) ltac:(kN_lia) ltac:(kN_lia) ltac:(kN_lia)).' % (q, P.ccoq(b), P.ccoq(c), P.ccoq(a), P.ccoq(a2), P.side_coq(rest))]
    return (q,newL,newR,mode),txt,'TL%s a=%s b=%s'%(q,P.cstr(a),P.cstr(b))
m_loop.anytime=True
