import planner8 as pl
from planner8 import mkrun, V, BLANK, lin
import phc
U=phc.U; UR=phc.UR; CTX=phc.CTX
EQS=[]      # (name, lin) equations produced by matchers
_fresh=[0]
def fresh(prefix='z'):
    _fresh[0]+=1
    return '%s%d'%(prefix,_fresh[0])
def reset():
    EQS.clear(); _fresh[0]=0
def is_run(t,blk):
    return isinstance(t,tuple) and t[0]=='run' and t[1]==tuple(blk)
def single(c):
    return len(c)==1 and c[0][1]==1
def parse_R(R):
    """R = (10)^j concrete pairs, optional run(UR,v), CTX..., returns (m_coq, j, v, rest_index_after_pairs_and_run) or None"""
    i=0;j=0
    while R[i:i+2]==[1,0]:
        j+=1; i+=2
    v=None
    if i<len(R) and is_run(R[i],UR) and single(R[i][2]):
        v=R[i][2][0][0]; i+=1
    if R[i:i+len(CTX)]!=CTX: return None
    m_coq=v if v else '0'
    for _ in range(j): m_coq='S (%s)'%m_coq
    return m_coq,j,v,i
def m_LN1(cfg):
    """([0;1]^^... F-loop: (0>>1>>0>>1>> [0;1]^^n *> l) <{{F}} ([1;0]^^m *> CTX) -->* (0>>1>> l) <{{F}} ([1;0]^^(m + 2*(S n)) *> CTX)"""
    q,L,R,mode=cfg
    if q!='F' or mode!='<': return None
    if not (len(L)>=5 and L[:4]==[0,1,0,1] and is_run(L[4],U) and single(L[4][2])): return None
    pr=parse_R(R)
    if pr is None: return None
    m_coq,j,v,i=pr
    n=L[4][2][0][0]
    nm=fresh('M')
    EQS.append((nm,'%s + 2 * (S %s)'%(m_coq,n)))
    L2=[0,1]+L[5:]
    R2=[('run',tuple(UR),((nm,1),))]+R[i:]
    import phc
    Rold=phc.side2coq(R)
    Rnew='[1;0]^^(%s) *> %s'%(m_coq,phc.side2coq(R[i:]))
    frag='change (%s) with (%s). follow (LN1 %s _ %s).'%(Rold,Rnew,n,m_coq)
    return (q,L2,R2,mode),frag,'LN1 loop over %s (m=%s)'%(n,m_coq)
m_LN1.anytime=True
