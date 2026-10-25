import sys
from sim1 import T
# halting patterns: B at 0 followed by 111 ; generally A at a 1.  Start from (A, cell=1).
# pattern: (state, tuple of (offset,bit) sorted, head offset implicit 0) ; cells relative to head.
def norm(q, cells):
    return (q, tuple(sorted(cells.items())))
start = norm(0, {0:1})
frontier = {start}
seen = set(frontier)
# preimages: for each (q0,c0)->(w,d,q) with q == current state
pre = {}
for (q0,c0),t in T.items():
    if t is None: continue
    w,d,q = t
    pre.setdefault(q,[]).append((q0,c0,w,1 if d=='R' else -1))
maxd=int(sys.argv[1]); cap=int(sys.argv[2])
for depth in range(1,maxd+1):
    new=set()
    for (q,cells) in frontier:
        cd=dict(cells)
        for (q0,c0,w,d) in pre.get(q,[]):
            # previous head at offset -d (relative to current head 0); the cell there after the step must be w
            p0=-d
            if p0 in cd and cd[p0]!=w: continue
            nc=dict(cd)
            nc[p0]=c0
            # re-center so that previous head is at 0
            sh={k-p0:v for k,v in nc.items()}
            n=norm(q0,sh)
            if n not in seen:
                seen.add(n); new.add(n)
    frontier=new
    print(depth,len(frontier),len(seen),flush=True)
    if not frontier: print('backward tree died: halting unreachable'); break
    if len(seen)>cap: print('cap'); break
