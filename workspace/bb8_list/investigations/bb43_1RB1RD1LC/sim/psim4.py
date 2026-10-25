from psim import *
import sys
n=int(sys.argv[1]); K=int(sys.argv[2])
st={'in':False}
def f(q,s,pos,tape):
    m=min(tape) if tape else 0
    inside = pos<=m+K
    r = inside and not st['in']
    st['in']=inside
    return r
run(n,f)
