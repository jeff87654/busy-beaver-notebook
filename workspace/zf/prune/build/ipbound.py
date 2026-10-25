"""IP-space prefix bound (as in the L3 proof): first RM op count after which gap >= depth + 12 + 3 holds
forever (gap = G0 + ndecnz, G0 = 16 as in rmrun.py), and min margin before it."""
import sys
from dag import extract, RM, walk
start, tbl, nodes, regidx = extract(sys.argv[1])
def depth(n, seen={}):
    if n in seen: return seen[n]
    c, d = nodes[n]
    v = 1 + max(depth(c[1]) if c[0] == 'node' else 0, depth(d[1]) if d[0] == 'node' else 0)
    seen[n] = v; return v
D = depth('main().0'); need = D + 12 + 3
rm = RM(nodes, 'main().0', len(regidx)); minm = 10**9; i = 0
while 16 + rm.ndecnz < need:
    leaf, d = walk(nodes, 'main().0', rm.P)
    m = 16 + rm.ndecnz - (d + (regidx[leaf[1]] + 1 if leaf[0] == 'op' else 0) + 3)
    minm = min(minm, m); rm.step(regidx); i += 1
print(sys.argv[1], 'max depth', D, 'prefix ops', i, 'min margin in prefix', minm)
