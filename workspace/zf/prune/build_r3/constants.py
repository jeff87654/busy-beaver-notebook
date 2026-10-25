"""L3-relevant constants of a candidate .tm: registers, DAG nodes, max consecutive car edges (dispatch
length), max walk depth, break/continue levels used, framework/DAG state counts."""
import sys
from dag import extract
for path in sys.argv[1:]:
    start, tbl, nodes, regidx = extract(path)
    def cz(e): return 1 + cz(nodes[e[1]][0]) if e[0] == 'node' else 0
    seen = {}
    def depth(n):
        if n in seen: return seen[n]
        c, d = nodes[n]
        v = 1 + max(depth(c[1]) if c[0] == 'node' else 0, depth(d[1]) if d[0] == 'node' else 0)
        seen[n] = v; return v
    br = max([e[1] for n in nodes.values() for e in n if e[0] == 'break'] + [0])
    co = max([e[1] for n in nodes.values() for e in n if e[0] == 'continue'] + [0])
    states = {s for (s, _) in tbl}
    fw = sum(1 for s in states if s[0].isdigit())
    print(f'{path}: states {len(states)} (framework {fw}, DAG {len(states)-fw}); regs {len(regidx)}; '
          f'max car run {max(cz(("node", n)) for n in nodes)}; max depth {depth("main().0")}; '
          f'max break {br}; max continue {co}')
